import os

from surya.input.load import load_from_folder, load_from_file
from surya.settings import settings as surya_settings


def load_pdfs_images(input_path, max_pages=None, start_page=None):
    if os.path.isdir(input_path):
        images, _, _ = load_from_folder(input_path, max_pages, start_page=start_page)
        highres_images, names, text_lines = load_from_folder(input_path, max_pages, dpi=surya_settings.IMAGE_DPI_HIGHRES,
                                                             load_text_lines=True, start_page=start_page)
    else:
        images, _, _ = load_from_file(input_path, max_pages, start_page=start_page)
        highres_images, names, text_lines = load_from_file(input_path, max_pages, dpi=surya_settings.IMAGE_DPI_HIGHRES,
                                                           load_text_lines=True, start_page=start_page)

    return images, highres_images, names, text_lines