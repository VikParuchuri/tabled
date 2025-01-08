from typing import List
from PIL import Image

from surya.input.pdflines import get_table_blocks
from surya.detection import DetectionPredictor
from surya.recognition import RecognitionPredictor
from surya.table_rec import TableRecPredictor, TableResult

from tabled.settings import settings


def get_cells(table_imgs, table_bboxes, image_sizes, text_lines, det_predictor: DetectionPredictor, detect_boxes=False, detector_batch_size=settings.DETECTOR_BATCH_SIZE):
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
    if len(to_inference_idxs) > 0:
        det_results = det_predictor([table_imgs[i] for i in to_inference_idxs], batch_size=detector_batch_size)
        for idx, det_result in zip(to_inference_idxs, det_results):
            cell_bboxes = [{"bbox": tb.bbox, "text": None} for tb in det_result.bboxes if tb.area > 0]
            table_cells[idx] = cell_bboxes

    return table_cells, needs_ocr


def recognize_tables(
        table_imgs: List[Image.Image],
        table_rec_predictor: TableRecPredictor,
        table_rec_batch_size=settings.TABLE_REC_BATCH_SIZE
) -> List[TableResult]:
    table_preds = table_rec_predictor(table_imgs, batch_size=table_rec_batch_size)
    return table_preds


