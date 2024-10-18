import re
from typing import List

from tabled.schema import SpanTableCell


def sort_within_cell(cells, tolerance=5):
    vertical_groups = {}
    for i, cell in enumerate(cells):
        group_key = round((cell.bbox[1] + cell.bbox[3]) / 2 / tolerance)
        if group_key not in vertical_groups:
            vertical_groups[group_key] = []
        vertical_groups[group_key].append((i, cell.bbox[0]))

    # Sort each group horizontally and flatten the groups into a single list
    sorted_cell_idxs = []
    for _, group in sorted(vertical_groups.items()):
        sorted_group = sorted(group, key=lambda x: x[1])
        sorted_cell_idxs.extend([idx for idx, _ in sorted_group])

    cell_order = [sorted_cell_idxs.index(i) for i in range(len(sorted_cell_idxs))]
    return cell_order


def sort_cells(cells: List[SpanTableCell]):
    cell_order = sort_within_cell(cells)
    for i, cell in enumerate(cells):
        cell.order = cell_order[i]
    cells.sort(key=lambda x: (x.row_ids[0], x.col_ids[0], x.order))
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
