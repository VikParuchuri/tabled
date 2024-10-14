import numpy as np
from sklearn.cluster import DBSCAN


def cluster_coords(coords, row_count):
    if len(coords) == 0:
        return []
    coords = np.array(sorted(set(coords))).reshape(-1, 1)

    clustering = DBSCAN(eps=.01, min_samples=max(2, row_count // 4)).fit(coords)
    clusters = clustering.labels_

    separators = []
    for label in set(clusters):
        clustered_points = coords[clusters == label]
        separators.append(np.mean(clustered_points))

    separators = sorted(separators)
    return separators


def find_column_separators(rows, page_size, round_factor=.002, min_count=1):
    left_edges = []
    right_edges = []
    centers = []

    boxes = [c.bbox for r in rows for c in r]

    for cell in boxes:
        ncell = [cell[0] / page_size[0], cell[1] / page_size[1], cell[2] / page_size[0], cell[3] / page_size[1]]
        left_edges.append(ncell[0] / round_factor * round_factor)
        right_edges.append(ncell[2] / round_factor * round_factor)
        centers.append((ncell[0] + ncell[2]) / 2 * round_factor / round_factor)

    left_edges = [l for l in left_edges if left_edges.count(l) > min_count]
    right_edges = [r for r in right_edges if right_edges.count(r) > min_count]
    centers = [c for c in centers if centers.count(c) > min_count]

    sorted_left = cluster_coords(left_edges, len(rows))
    sorted_right = cluster_coords(right_edges, len(rows))
    sorted_center = cluster_coords(centers, len(rows))

    # Find list with minimum length
    separators = max([sorted_left, sorted_right, sorted_center], key=len)
    separators.append(1)
    separators.insert(0, 0)
    return separators


def assign_cells_to_columns(rows, page_size, round_factor=.002, tolerance=.01):
    separators = find_column_separators(rows, page_size, round_factor=round_factor)
    additional_column_index = 0
    row_dicts = []

    for row in rows:
        new_row = {}
        last_col_index = -1
        for cell in row:
            left_edge = cell.bbox[0] / page_size[0]
            column_index = -1
            for i, separator in enumerate(separators):
                if left_edge - tolerance < separator and last_col_index < i:
                    column_index = i
                    break
            if column_index == -1:
                column_index = len(separators) + additional_column_index
                additional_column_index += 1
            new_row[column_index] = cell
            last_col_index = column_index
        additional_column_index = 0
        row_dicts.append(new_row)

    cells = []
    for row_idx, row in enumerate(row_dicts):
        column = 0
        for col_idx in sorted(row.keys()):
            cell = row[col_idx]
            cell.row_ids = [row_idx]
            cell.col_ids = [column]
            cells.append(cell)
            column += 1

    return cells