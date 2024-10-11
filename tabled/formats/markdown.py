import re
from typing import List

from tabulate import tabulate

from tabled.schema import SpanTableCell


def sort_cells(cells: List[SpanTableCell]):
    cells.sort(key=lambda x: (x.row_ids[0], x.col_ids[0]))
    return cells


def replace_dots(text):
    dot_pattern = re.compile(r'(\s*\.\s*){4,}')
    dot_multiline_pattern = re.compile(r'.*(\s*\.\s*){4,}.*', re.DOTALL)

    if dot_multiline_pattern.match(text):
        text = dot_pattern.sub(' ', text)
    return text


def replace_newlines(text):
    # Replace all newlines
    newline_pattern = re.compile(r'[\r\n]+')
    return newline_pattern.sub(' ', text).strip()


def replace_special_chars(text):
    return text.replace("|", " ").replace("-", "")


def replace_all(text):
    return replace_special_chars(replace_newlines(replace_dots(text)))


def markdown_format(cells: List[SpanTableCell]):
    md_rows = []
    cells = sort_cells(cells)
    unique_rows = set([cell.row_ids[0] for cell in cells])
    unique_cols = set([cell.col_ids[0] for cell in cells])
    for row in unique_rows:
        md_row = []
        for col in unique_cols:
            cell = " ".join([cell.text for cell in cells if cell.row_ids[0] == row and cell.col_ids[0] == col])
            cell = replace_all(cell)
            md_row.append(cell)
        md_rows.append(md_row)

    md = tabulate(md_rows, headers="firstrow", tablefmt="github", disable_numparse=True)
    return md
