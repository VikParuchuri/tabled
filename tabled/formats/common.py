import re
from typing import List

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
