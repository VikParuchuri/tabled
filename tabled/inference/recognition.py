from typing import List

from surya.detection import batch_text_detection
from surya.input.pdflines import get_table_blocks
from surya.ocr import run_recognition
from surya.schema import TableResult
from surya.tables import batch_table_recognition


def get_cells(table_imgs, table_bboxes, image_sizes, text_lines, models, detect_boxes=False):
    det_model, det_processor = models
    table_cells = []
    needs_ocr = []

    to_inference_idxs = []
    for idx, (highres_bbox, text_line, image_size) in enumerate(zip(table_bboxes, text_lines, image_sizes)):
        # The text cells inside each table
        table_blocks = get_table_blocks([highres_bbox], text_line, image_size)[0] if text_line is not None else None

        if text_line is None or detect_boxes or len(table_blocks) == 0:
            to_inference_idxs.append(idx)
            table_cells.append(None)
            needs_ocr.append(True)
        else:
            table_cells.append(table_blocks)
            needs_ocr.append(False)

    # Inference tables that need it
    det_results = batch_text_detection([table_imgs[i] for i in to_inference_idxs], det_model, det_processor)
    for idx, det_result in zip(to_inference_idxs, det_results):
        cell_bboxes = [{"bbox": tb.bbox, "text": None} for tb in det_result.bboxes]
        table_cells[idx] = cell_bboxes

    return table_cells, needs_ocr


def recognize_tables(table_imgs, table_cells, needs_ocr: List[bool], models) -> List[TableResult]:
    table_rec_model, table_rec_processor, ocr_model, ocr_processor = models

    if sum(needs_ocr) > 0:
        needs_ocr_idx = [idx for idx, needs in enumerate(needs_ocr) if needs]
        ocr_images = [img for img, needs in zip(table_imgs, needs_ocr) if needs]
        ocr_cells = [[c["bbox"] for c in cells] for cells, needs in zip(table_cells, needs_ocr) if needs]
        ocr_langs = [None] * len(ocr_images)

        ocr_predictions = run_recognition(ocr_images, ocr_langs, ocr_model, ocr_processor, bboxes=ocr_cells)

        # Assign text to correct spot
        for orig_idx, ocr_pred in zip(needs_ocr_idx, ocr_predictions):
            for ocr_line, cell in zip(ocr_pred.text_lines, table_cells[orig_idx]):
                cell["text"] = ocr_line.text

    table_preds = batch_table_recognition(table_imgs, table_cells, table_rec_model, table_rec_processor)
    return table_preds


