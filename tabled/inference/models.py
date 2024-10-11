from surya.model.detection.model import load_model as load_det_model, load_processor as load_det_processor
from surya.model.recognition.model import load_model as load_rec_model
from surya.model.recognition.processor import load_processor as load_rec_processor
from surya.model.table_rec.model import load_model as load_table_rec_model
from surya.model.table_rec.processor import load_processor as load_table_rec_processor
from surya.settings import settings as surya_settings


def load_detection_models():
    det_model = load_det_model()
    det_processor = load_det_processor()
    layout_model = load_det_model(checkpoint=surya_settings.LAYOUT_MODEL_CHECKPOINT)
    layout_processor = load_det_processor(checkpoint=surya_settings.LAYOUT_MODEL_CHECKPOINT)
    return det_model, det_processor, layout_model, layout_processor


def load_recognition_models():
    table_rec_model = load_table_rec_model()
    table_rec_processor = load_table_rec_processor()
    rec_model = load_rec_model()
    rec_processor = load_rec_processor()
    return table_rec_model, table_rec_processor, rec_model, rec_processor