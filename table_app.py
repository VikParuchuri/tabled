import os

from tabled.assignment import assign_rows_columns
from tabled.fileinput import load_pdfs_images
from tabled.formats import formatter
from tabled.inference.detection import detect_tables
from tabled.inference.recognition import get_cells, recognize_tables

os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
os.environ["IN_STREAMLIT"] = "true"
import pypdfium2

import io
import tempfile
from PIL import Image

import streamlit as st
from tabled.inference.models import load_detection_models, load_recognition_models, load_layout_models


@st.cache_resource()
def load_models():
    return load_detection_models(), load_recognition_models(), load_layout_models()


def run_table_rec(image, highres_image, text_line, models, skip_detection=False, detect_boxes=False, out_format='markdown'):
    if not skip_detection:
        table_imgs, table_bboxes, _ = detect_tables([image], [highres_image], models[2])
    else:
        table_imgs = [highres_image]
        table_bboxes = [[0, 0, highres_image.size[0], highres_image.size[1]]]

    table_text_lines = [text_line] * len(table_imgs)
    highres_image_sizes = [highres_image.size] * len(table_imgs)
    cells, needs_ocr = get_cells(table_imgs, table_bboxes, highres_image_sizes, table_text_lines, models[0], detect_boxes=detect_boxes)

    table_rec = recognize_tables(table_imgs, cells, needs_ocr, models[1])
    cells = [assign_rows_columns(tr, im_size) for tr, im_size in zip(table_rec, highres_image_sizes)]

    out_data = []
    for idx, (cell, pred, table_img) in enumerate(zip(cells, table_rec, table_imgs)):
        formatted_output, _ = formatter(out_format, cell)
        out_data.append((formatted_output, table_img))
    return out_data


def open_pdf(pdf_file):
    stream = io.BytesIO(pdf_file.getvalue())
    return pypdfium2.PdfDocument(stream)


@st.cache_data()
def get_page_image(pdf_file, page_num, dpi=96):
    doc = open_pdf(pdf_file)
    renderer = doc.render(
        pypdfium2.PdfBitmap.to_pil,
        page_indices=[page_num - 1],
        scale=dpi / 72,
    )
    png = list(renderer)[0]
    png_image = png.convert("RGB")
    return png_image


@st.cache_data()
def page_count(pdf_file):
    doc = open_pdf(pdf_file)
    return len(doc)


st.set_page_config(layout="wide")

models = load_models()


st.markdown("""
# Tabled Demo

This app will let you try tabled, a table detection and recognition model.  It will detect and recognize the tables.

Find the project [here](https://github.com/VikParuchuri/tabled).
""")

in_file = st.sidebar.file_uploader("PDF file or image:", type=["pdf", "png", "jpg", "jpeg", "gif", "webp"])
skip_detection = st.sidebar.checkbox("Skip table detection", help="Use this if tables are already cropped (the whole PDF page or image is a table)", value=False)
detect_boxes = st.sidebar.checkbox("Detect cell boxes", help="Detect table cell boxes vs extract from PDF.  Will also run OCR.", value=False)
out_format = st.sidebar.selectbox('Output Format', ['Markdown', 'HTML', 'CSV']).lower()

if in_file is None:
    st.stop()

filetype = in_file.type
col = st.columns(1)[0]
container = col.container()

if "pdf" in filetype:
    page_count = page_count(in_file)
    page_number = st.sidebar.number_input(f"Page number out of {page_count}:", min_value=1, value=1,
                                          max_value=page_count)

    pil_image = get_page_image(in_file, page_number, 96)
else:
    pil_image = Image.open(in_file).convert("RGB")
    pil_image_highres = pil_image
    page_number = 1

with col:
    st.image(pil_image, caption="PDF file (preview)", use_container_width=True)

    run_marker = st.sidebar.button("Run Tabled")

if not run_marker:
    st.stop()

# Run Tabled
file_ext = in_file.name.rsplit(".")[-1]
with tempfile.NamedTemporaryFile(suffix=file_ext) as temp_input:
    temp_input.write(in_file.getvalue())
    temp_input.seek(0)
    filename = temp_input.name
    images, highres_images, names, text_lines = load_pdfs_images(filename, max_pages=1, start_page=page_number - 1)
    out_data = run_table_rec(images[0], highres_images[0], text_lines[0], models, skip_detection=skip_detection, detect_boxes=detect_boxes, out_format=out_format)

for idx, (formatted_output, table_img) in enumerate(out_data):
    container.markdown(f"## Table {idx}")
    container.image(table_img, caption=f"Table {idx}", use_container_width=True)
    if out_format == 'markdown':
        container.markdown(formatted_output)
    elif out_format == 'html':
        container.html(formatted_output)
    container.code(formatted_output)
    container.divider()

