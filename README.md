# Tabled

Tabled is a small library for detecting and extracting tables.  It uses [surya](https://www.github.com/VikParuchuri/surya) to first find all the tables in a PDF, then identifies the rows/columns, and turns the cells into either markdown or html.

## Examples


## Community

[Discord](https://discord.gg//KuZwXNGnfH) is where we discuss future development.`

# Hosted API

There is a hosted API for tabled available [here](https://www.datalab.to/):

- Works with PDF, images, word docs, and powerpoints
- Consistent speed, with no latency spikes
- High reliability and uptime

# Commercial usage

I want tabled to be as widely accessible as possible, while still funding my development/training costs. Research and personal usage is always okay, but there are some restrictions on commercial usage.

The weights for the models are licensed `cc-by-nc-sa-4.0`, but I will waive that for any organization under $5M USD in gross revenue in the most recent 12-month period AND under $5M in lifetime VC/angel funding raised. You also must not be competitive with the [Datalab API](https://www.datalab.to/).  If you want to remove the GPL license requirements (dual-license) and/or use the weights commercially over the revenue limit, check out the options [here](https://www.datalab.to).

# Installation

You'll need python 3.10+ and PyTorch. You may need to install the CPU version of torch first if you're not using a Mac or a GPU machine.  See [here](https://pytorch.org/get-started/locally/) for more details.

Install with:

```shell
pip install tabled-pdf
```

Post-install:

- Inspect the settings in `tabled/settings.py`.  You can override any settings with environment variables.
- Your torch device will be automatically detected, but you can override this.  For example, `TORCH_DEVICE=cuda`.
- Model weights will automatically download the first time you run tabled.

# Usage

```shell
tabled DATA_PATH
```

- `DATA_PATH` can be an image, pdf, or folder of images/pdfs
- `--skip_detection` means that the images you pass in are all cropped tables and don't need any detection.
- `--detect_boxes` by default, tabled will attempt to pull cell information out of the pdf.  If you instead want cells to be detected by a detection model, specify this (usually you only need this with pdfs that have bad embedded text).
- `--save_images` specifies that images of detected rows/columns and cells should be saved.

The `results.json` file will contain a json dictionary where the keys are the input filenames without extensions.  Each value will be a list of dictionaries, one per page of the input document.  Each page dictionary contains:

- `text_lines` - the detected text and bounding boxes for each line
  - `text` - the text in the line
  - `confidence` - the confidence of the model in the detected text (0-1)
  - `polygon` - the polygon for the text line in (x1, y1), (x2, y2), (x3, y3), (x4, y4) format.  The points are in clockwise order from the top left.
  - `bbox` - the axis-aligned rectangle for the text line in (x1, y1, x2, y2) format.  (x1, y1) is the top left corner, and (x2, y2) is the bottom right corner.
- `languages` - the languages specified for the page
- `page` - the page number in the file
- `image_bbox` - the bbox for the image in (x1, y1, x2, y2) format.  (x1, y1) is the top left corner, and (x2, y2) is the bottom right corner.  All line bboxes will be contained within this bbox.

## Interactive App

I've included a streamlit app that lets you interactively try tabled on images or PDF files.  Run it with:

```shell
pip install streamlit
tabled_gui
```