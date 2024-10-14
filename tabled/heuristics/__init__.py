from typing import List

from tabled.heuristics.cells import assign_cells_to_columns
from tabled.schema import SpanTableCell


def heuristic_layout(table_cells: List[SpanTableCell], page_size, row_tol=.01) -> List[SpanTableCell]:
    table_rows = []
    table_row = []
    y_top = None
    y_bottom = None
    for cell in table_cells:
        normed_y_start = cell.bbox[1] / page_size[1]
        normed_y_end = cell.bbox[3] / page_size[1]

        if y_top is None:
            y_top = normed_y_start
        if y_bottom is None:
            y_bottom = normed_y_end

        y_dist = min(abs(normed_y_start - y_bottom), abs(normed_y_end - y_bottom))
        if y_dist < row_tol:
            table_row.append(cell)
        else:
            # New row
            if len(table_row) > 0:
                table_rows.append(table_row)
            table_row = [cell]
            y_top = normed_y_start
            y_bottom = normed_y_end
    if len(table_row) > 0:
        table_rows.append(table_row)

    return assign_cells_to_columns(table_rows, page_size)