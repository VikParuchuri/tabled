from surya.postprocessing.util import rescale_bbox
from tabled.settings import settings
from surya.common.polygon import PolygonBox


def merge_boxes(box1, box2):
    return [min(box1[0], box2[0]), min(box1[1], box2[1]), max(box1[2], box2[2]), max(box1[3], box2[3])]


def merge_tables(page_table_boxes):
    # Merge tables that are next to each other
    expansion_factor = 1.02
    shrink_factor = .98
    ignore_boxes = set()
    for i in range(len(page_table_boxes)):
        if i in ignore_boxes:
            continue
        for j in range(i + 1, len(page_table_boxes)):
            if j in ignore_boxes:
                continue
            expanded_box1 = [page_table_boxes[i][0] * shrink_factor, page_table_boxes[i][1],
                             page_table_boxes[i][2] * expansion_factor, page_table_boxes[i][3]]
            expanded_box2 = [page_table_boxes[j][0] * shrink_factor, page_table_boxes[j][1],
                             page_table_boxes[j][2] * expansion_factor, page_table_boxes[j][3]]
            if PolygonBox(polygon=expanded_box1).intersection_pct(PolygonBox(polygon=expanded_box2)) > 0:
                page_table_boxes[i] = merge_boxes(page_table_boxes[i], page_table_boxes[j])
                ignore_boxes.add(j)

    return [b for i, b in enumerate(page_table_boxes) if i not in ignore_boxes]


def detect_tables(images, highres_images, layout_predictor, layout_batch_size=settings.LAYOUT_BATCH_SIZE):
    layout_predictions = layout_predictor(images, batch_size=layout_batch_size)

    table_imgs = []
    table_counts = []
    table_bboxes = []

    for layout_pred, img, highres_img in zip(layout_predictions, images, highres_images):
        # The bbox for the entire table
        bbox = [l.bbox for l in layout_pred.bboxes if l.label == "Table"]

        if len(bbox) == 0:
            table_counts.append(0)
            continue

        page_table_imgs = []
        highres_bbox = []

        # Merge tables that are next to each other
        bbox = merge_tables(bbox)

        # Number of tables per page
        table_counts.append(len(bbox))

        for bb in bbox:
            highres_bb = rescale_bbox(bb, img.size, highres_img.size)
            page_table_imgs.append(highres_img.crop(highres_bb))
            highres_bbox.append(highres_bb)

        table_imgs.extend(page_table_imgs)
        table_bboxes.extend(highres_bbox)

    return table_imgs, table_bboxes, table_counts