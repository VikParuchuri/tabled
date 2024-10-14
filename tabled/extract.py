from typing import List

from tabled.assignment import assign_rows_columns
from tabled.inference.detection import detect_tables
from tabled.inference.recognition import get_cells, recognize_tables
from tabled.schema import ExtractPageResult


def extract_tables(images, highres_images, text_lines, det_models, rec_models, skip_detection=False, detect_boxes=False) -> List[ExtractPageResult]:
    if not skip_detection:
        table_imgs, table_bboxes, table_counts = detect_tables(images, highres_images, det_models)
    else:
        table_imgs = highres_images
        table_bboxes = [[0, 0, img.size[0], img.size[1]] for img in highres_images]
        table_counts = [1] * len(highres_images)

    table_text_lines = []
    highres_image_sizes = []
    for i, tc in enumerate(table_counts):
        table_text_lines.extend([text_lines[i]] * tc)
        highres_image_sizes.extend([highres_images[i].size] * tc)

    cells, needs_ocr = get_cells(table_imgs, table_bboxes, highres_image_sizes, table_text_lines, det_models[:2], detect_boxes=detect_boxes)

    table_rec = recognize_tables(table_imgs, cells, needs_ocr, rec_models)
    cells = [assign_rows_columns(tr) for tr in table_rec]

    results = []
    counter = 0
    for count in table_counts:
        page_start = counter
        page_end = counter + count
        results.append(ExtractPageResult(
            table_imgs=table_imgs[page_start:page_end],
            cells=cells[page_start:page_end],
            rows_cols=table_rec[page_start:page_end]
        ))
        counter += count

    assert len(results) == len(images)
    return results
