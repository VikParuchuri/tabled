import argparse
import json
import time

import datasets
from surya.input.pdflines import get_table_blocks
from tabulate import tabulate
from tqdm import tqdm
from scoring import score_table
from tabled.assignment import assign_rows_columns

from tabled.formats import formatter
from tabled.inference.models import load_recognition_models
from tabled.inference.recognition import recognize_tables


def main():
    parser = argparse.ArgumentParser(description="Benchmark table conversion.")
    parser.add_argument("out_file", help="Output filename for results")
    parser.add_argument("--dataset", type=str, help="Dataset to use", default="vikp/table_bench2")
    args = parser.parse_args()

    ds = datasets.load_dataset(args.dataset, split="train")

    rec_models = load_recognition_models()

    results = []
    table_imgs = []
    table_blocks = []
    image_sizes = []
    for i in range(len(ds)):
        row = ds[i]
        line_data = json.loads(row["text_lines"])
        table_bbox = row["table_bbox"]
        image_size = row["page_size"]
        table_img = row["table_image"]

        table_block = get_table_blocks([table_bbox], line_data, image_size)[0]
        table_imgs.append(table_img)
        table_blocks.append(table_block)
        image_sizes.append(image_size)

    start = time.time()
    table_rec = recognize_tables(table_imgs, table_blocks, [False] * len(table_imgs), rec_models)
    total_time = time.time() - start
    cells = [assign_rows_columns(tr, im_size) for tr, im_size in zip(table_rec, image_sizes)]

    for i in range(len(ds)):
        row = ds[i]
        table_cells = cells[i]
        table_bbox = row["table_bbox"]
        gpt4_table = json.loads(row["gpt_4_table"])["markdown_table"]

        table_markdown, _ = formatter("markdown", table_cells)

        results.append({
            "score": score_table(table_markdown, gpt4_table),
            "arxiv_id": row["arxiv_id"],
            "page_idx": row["page_idx"],
            "marker_table": table_markdown,
            "gpt4_table": gpt4_table,
            "table_bbox": table_bbox
        })

    avg_score = sum([r["score"] for r in results]) / len(results)
    headers = ["Avg score", "Time per table", "Total tables"]
    data = [f"{avg_score:.3f}", f"{total_time / len(ds):.3f}", len(ds)]

    table = tabulate([data], headers=headers, tablefmt="github")
    print(table)
    print("Avg score computed by aligning table cell text with GPT-4 table cell text.")

    with open(args.out_file, "w+") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    main()