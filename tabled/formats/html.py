from typing import List

from tabulate import tabulate

from tabled.formats.common import sort_cells, replace_dots, replace_newlines
from tabled.schema import SpanTableCell


def replace_all(text):
    return replace_newlines(replace_dots(text))


def html_format(cells: List[SpanTableCell]):
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

    headers = "firstrow" if len(cells) > 1 else ""
    md = tabulate(md_rows, headers=headers, tablefmt="html", disable_numparse=True)
    return md
