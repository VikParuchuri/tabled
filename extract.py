import json
from collections import defaultdict

import copy
import os

import click
from surya.postprocessing.heatmap import draw_bboxes_on_image

from tabled.extract import extract_tables
from tabled.formats import formatter
from tabled.input.fileinput import load_pdfs_images
from tabled.inference.models import load_detection_models, load_recognition_models, load_layout_models


@click.command(help="Extract tables from PDFs")
@click.argument("in_path", type=click.Path(exists=True))
@click.argument("out_folder", type=click.Path())
@click.option("--save_json", is_flag=True, help="Save row/column/cell information in json format")
@click.option("--save_debug_images", is_flag=True, help="Save images for debugging")
@click.option("--skip_detection", is_flag=True, help="Skip table detection")
@click.option("--detect_cell_boxes", is_flag=True, help="Detect table cell boxes vs extract from PDF.  Will also run OCR.")
@click.option("--format", type=click.Choice(["markdown", "csv", "html"]), default="markdown")
def main(in_path, out_folder, save_json, save_debug_images, skip_detection, detect_cell_boxes, format):
    os.makedirs(out_folder, exist_ok=True)
    images, highres_images, names, text_lines = load_pdfs_images(in_path)
    pnums = []
    prev_name = None
    for i, name in enumerate(names):
        if prev_name is None or prev_name != name:
            pnums.append(0)
        else:
            pnums.append(pnums[-1] + 1)

        prev_name = name

    det_models = load_detection_models()
    rec_models = load_recognition_models()
    layout_models = load_layout_models()

    page_results = extract_tables(images, highres_images, text_lines, det_models, layout_models, rec_models, skip_detection=skip_detection, detect_boxes=detect_cell_boxes)

    out_json = defaultdict(list)
    for name, pnum, result in zip(names, pnums, page_results):
        for i in range(result.total):
            page_cells = result.cells[i]
            page_rc = result.rows_cols[i]
            img = result.table_imgs[i]

            base_path = os.path.join(out_folder, name)
            os.makedirs(base_path, exist_ok=True)

            formatted_result, ext = formatter(format, page_cells)
            base_name = f"page{pnum}_table{i}"
            with open(os.path.join(base_path, f"{base_name}.{ext}"), "w+", encoding="utf-8") as f:
                f.write(formatted_result)

            img.save(os.path.join(base_path, f"{base_name}.png"))

            res = {
                "cells": [c.model_dump() for c in page_cells],
                "rows": [r.model_dump() for r in page_rc.rows],
                "cols": [c.model_dump() for c in page_rc.cols],
                "bbox": result.bboxes[i].bbox,
                "image_bbox": result.image_bboxes[i].bbox,
                "pnum": pnum,
                "tnum": i
            }
            out_json[name].append(res)

            if save_debug_images:
                boxes = [l.bbox for l in page_cells]
                labels = [l.label for l in page_cells]
                bbox_image = draw_bboxes_on_image(boxes, copy.deepcopy(img), labels=labels, label_font_size=20)
                bbox_image.save(os.path.join(base_path, f"{base_name}_cells.png"))

                rows = [l.bbox for l in page_rc.rows]
                cols = [l.bbox for l in page_rc.cols]
                row_labels = [f"Row {l.row_id}" for l in page_rc.rows]
                col_labels = [f"Col {l.col_id}" for l in page_rc.cols]

                rc_image = copy.deepcopy(img)
                rc_image = draw_bboxes_on_image(rows, rc_image, labels=row_labels, label_font_size=20, color="blue")
                rc_image = draw_bboxes_on_image(cols, rc_image, labels=col_labels, label_font_size=20, color="red")
                rc_image.save(os.path.join(base_path, f"{base_name}_rc.png"))

    if save_json:
        with open(os.path.join(out_folder, "result.json"), "w+", encoding="utf-8") as f:
            json.dump(out_json, f, ensure_ascii=False)


if __name__ == "__main__":
    main()
