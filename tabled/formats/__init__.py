from tabled.formats.csv import csv_format
from tabled.formats.html import html_format
from tabled.formats.markdown import markdown_format


def formatter(format, page_cells, **tabulate_kwargs):
    if format == "csv":
        return csv_format(page_cells), "csv"
    elif format == "markdown":
        return markdown_format(page_cells, **tabulate_kwargs), "md"
    elif format == "html":
        return html_format(page_cells, **tabulate_kwargs), "html"
    else:
        raise ValueError(f"Invalid format: {format}")