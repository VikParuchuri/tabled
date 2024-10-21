from typing import List, Optional, Any

from pydantic import BaseModel, model_validator
from surya.schema import Bbox, TableResult


def str_join(list, char=","):
    return char.join([str(x) for x in list])


class SpanTableCell(Bbox):
    text: str
    row_ids: List[Optional[int]]
    col_ids: List[Optional[int]]
    order: Optional[int] = None

    def intersection_x_pct(self, other):
        if self.width == 0:
            return 0

        x_overlap = max(0, min(self.bbox[2], other.bbox[2]) - max(self.bbox[0], other.bbox[0]))
        return x_overlap / self.width


    def intersection_y_pct(self, other):
        if self.height == 0:
            return 0

        y_overlap = max(0, min(self.bbox[3], other.bbox[3]) - max(self.bbox[1], other.bbox[1]))
        return y_overlap / self.height

    @property
    def label(self):
        return f"{str_join(self.row_ids)}-{str_join(self.col_ids)}"

    def center_x_distance(self, other):
        return abs(self.center[0] - other.center[0])

    def center_y_distance(self, other):
        return abs(self.center[1] - other.center[1])


class ExtractPageResult(BaseModel):
    cells: List[List[SpanTableCell]]
    rows_cols: List[TableResult]
    table_imgs: List[Any]
    bboxes: List[Bbox] # Bbox of the table
    image_bboxes: List[Bbox] # Bbox of the image/page table is inside

    @model_validator(mode="after")
    def check_cells(self):
        assert len(self.cells) == len(self.table_imgs), "Cells and table images must be the same length"
        assert len(self.cells) == len(self.rows_cols), "Cells and rows/cols must be the same length"
        return self

    @property
    def total(self):
        return len(self.cells)
