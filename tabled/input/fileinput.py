import os
from typing import List

from surya.input.load import load_from_folder, load_from_file
from surya.settings import settings as surya_settings


def load_pdfs_images(input_path, page_range: List[int] | None = None):
    if os.path.isdir(input_path):
        images, _ = load_from_folder(input_path, page_range)
        highres_images, names = load_from_folder(input_path, page_range, dpi=surya_settings.IMAGE_DPI_HIGHRES)
    else:
        images, _, _ = load_from_file(input_path, page_range)
        highres_images, names = load_from_file(input_path, page_range, dpi=surya_settings.IMAGE_DPI_HIGHRES)

    return images, highres_images, names