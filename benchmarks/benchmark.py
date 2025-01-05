import json
import time
import click
import datasets
from tabulate import tabulate
from bs4 import BeautifulSoup
from tqdm import tqdm

from scoring import batched_TEDS

from tabled.assignment import assign_rows_columns
from tabled.formats import formatter
from tabled.formats.common import replace_newlines
from tabled.inference.models import load_recognition_models, load_detection_models, load_layout_models
from tabled.inference.recognition import recognize_tables, get_cells


@click.command()
@click.argument("out_file", type=str)
@click.option("--dataset", type=str, default="tarun-menta/fintabnet-html-test", help="Dataset to use")
@click.option("--max", type=int, default=None, help="Max number of tables to process")
def main(out_file, dataset, max):
    ds = datasets.load_dataset(dataset, split="train")
    ds = ds.shuffle(seed=0)

    detection_models, rec_models= load_detection_models(), load_recognition_models()

    results = []
    table_imgs = []
    image_sizes = []
    table_bboxes = []
    text_lines = []
    iterations = len(ds)
    if max is not None:
        iterations = min(max, len(ds))
    for i in tqdm(range(iterations), desc='Preparing Inputs'):
        row = ds[i]
        table_img = row['highres_table_img']
        line_data = row['pdftext_lines']
        image_size = row['highres_img'].size
        table_bbox = row['highres_table_bbox']

        table_imgs.append(table_img)
        image_sizes.append(image_size)
        table_bboxes.append(table_bbox)
        text_lines.append(line_data)

    start = time.time()
    table_cells, needs_ocr = get_cells(table_imgs, table_bboxes, image_sizes, text_lines, detection_models, detect_boxes=False)
    table_rec = recognize_tables(table_imgs, table_cells, needs_ocr, rec_models)
    total_time = time.time() - start
    cells = [assign_rows_columns(tr, im_size) for tr, im_size in zip(table_rec, image_sizes)]

    for i in range(iterations):
        row = ds[i]
        table_cells = cells[i]
        gt_table_html = row['orig_html']

        marker_table_html, _ = formatter("html", table_cells, numalign=None, stralign=None, headers="")
        marker_table_soup = BeautifulSoup(marker_table_html, 'html.parser')
        marker_table_soup.find('tbody').unwrap()    #Tabulate wraps the table in <tbody> which fintabnet data doesn't
        marker_table_html = str(marker_table_soup)
        
        results.append({
            "marker_table": marker_table_html,
            "gt_table": gt_table_html,
        })

    scores = batched_TEDS([r['gt_table'] for r in results], [r['marker_table'] for r in results])
    for result, score in zip(results, scores):
        result.update({'score': score})

    avg_score = sum([r["score"] for r in results]) / len(results)
    headers = ["Avg score", "Time per table", "Total tables"]
    data = [f"{avg_score:.3f}", f"{total_time / iterations:.3f}", iterations]

    table = tabulate([data], headers=headers, tablefmt="github")
    print(table)
    print("Avg score computed by comparing tabled predicted HTML with original HTML")

    with open(out_file, "w+") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    main()