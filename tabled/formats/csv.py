from typing import List

from tabulate import tabulate

from tabled.formats.common import sort_cells, replace_dots, replace_newlines
from tabled.schema import SpanTableCell
import csv
import io


def replace_all(text):
    return replace_newlines(replace_dots(text))


def csv_format(cells: List[SpanTableCell]):
    cells = sort_cells(cells)
    unique_rows = set([cell.row_ids[0] for cell in cells])
    unique_cols = set([cell.col_ids[0] for cell in cells])
    buff = io.StringIO()
    writer = csv.writer(buff)
    for row in unique_rows:
        text_row = []
        for col in unique_cols:
            cell = " ".join([cell.text for cell in cells if cell.row_ids[0] == row and cell.col_ids[0] == col])
            cell = replace_all(cell)
            text_row.append(cell)
        writer.writerow(text_row)

    csv_str = buff.getvalue()
    return csv_str
