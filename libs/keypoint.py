from pathlib import Path
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import numpy as np
import json


DEFAULT_LINE_COLOR = QColor(0, 255, 0, 128)
DEFAULT_FILL_COLOR = QColor(255, 0, 0, 128)
DEFAULT_SELECT_LINE_COLOR = QColor(255, 255, 255)
DEFAULT_SELECT_FILL_COLOR = QColor(0, 128, 255, 155)
DEFAULT_VERTEX_FILL_COLOR = QColor(0, 255, 0, 255)
DEFAULT_HVERTEX_FILL_COLOR = QColor(255, 0, 0)

SKELETON_COLORS = (
    QColor(255, 0, 85),
    QColor(255, 0, 0),
    QColor(255,  85, 0),
    QColor(255, 170, 0),
    QColor(255, 255, 0),
    QColor(170, 255, 0),
    QColor(85, 255, 0),
    QColor(0, 255, 0),
    QColor(255, 0, 0),
    QColor(0, 255, 85),
    QColor(0, 255, 170),
    QColor(0, 255, 255),
    QColor(0, 170, 255),
    QColor(0, 85, 255),
    QColor(0, 0, 255),
    QColor(255, 0, 170),
    QColor(170, 0, 255),
    QColor(255, 0, 255),
    QColor(85, 0, 255),
    QColor(85, 85, 255),
)

KEY_POINT_COLORS = (
    QColor(255, 0,    85),
    QColor(255, 0, 0),
    QColor(255,    85, 0),
    QColor(255,   170, 0),
    QColor(255,   255, 0),
    QColor(170,   255, 0),
    QColor(85,   255, 0),
    QColor(0,   255, 0),
    QColor(0,   255,    85),
    QColor(0,   255,   170),
    QColor(0,   255,   255),
    QColor(0,   170,   255),
    QColor(0,    85,   255),
    QColor(0,     0,   255),
    QColor(255,     0,   170),
    QColor(170,     0,   255),
    QColor(255,     0,   255),
    QColor(85,     0,   255)
)

class KeyPoint:
    KEY_POINT_NAMES = (
        "nose","left_eye","right_eye","left_ear","right_ear", "neck",
        "left_shoulder","right_shoulder","left_elbow","right_elbow",
        "left_wrist","right_wrist","left_hip","right_hip",
        "left_knee","right_knee","left_ankle","right_ankle"
    )
    KEY_POINT_PAIRS = (
        ("nose", "left_eye"),
        ("nose", "right_eye"),
        ("left_eye", "left_ear"),
        ("right_eye", "right_ear"),

        ("neck", "nose"),
        ("neck", "right_shoulder"),
        ("neck", "left_shoulder"),

        ("left_ear", "left_shoulder"),
        ("right_ear", "right_shoulder"),
        ("left_shoulder", "left_elbow"),
        ("right_shoulder", "right_elbow"),

        ("left_elbow", "left_wrist"),
        ("right_elbow", "right_wrist"),

        ("left_shoulder", "left_hip"),
        ("right_shoulder", "right_hip"),

        ("left_hip", "right_hip"),
        ("left_hip", "left_knee"),
        ("right_hip", "right_knee"),
        ("left_knee", "left_ankle"),
        ("right_knee", "right_ankle"),
    )
    P_SQUARE, P_ROUND = range(2)
    KEY_POINT_NUM = 18
    vertex_fill_color = DEFAULT_VERTEX_FILL_COLOR
    point_type = P_ROUND
    point_size = 8
    scale = 1.0

    def __init__(self, keypoint_num=None, keypoints=None):
        self.reset_keypoints()
        self.keypoint_index = 0
        self.changed = False
        if keypoint_num:
            assert len(keypoints) % 3 == 0
            for i in range(len(keypoints)):
                x, y, num = keypoints[i*3:(i + 1) * 3]
                if num:
                    self.keypoints[KeyPoint.KEY_POINT_NAMES[i]] = QPoint(x, y)

    def set_wh(self, w, h):
        self.height = h
        self.width = w

    def load(self, file_name):
        pass

    def is_end(self) -> bool:
        return self.keypoint_index == KeyPoint.KEY_POINT_NUM

    def save(self, file_name: Path):
        zero = (0, 0, 0)
        k = self.keypoints
        num_keypoints = len([i for i in KeyPoint.KEY_POINT_NAMES if k[i] is not None])
        keypoints = [zero if k[i] is None else (k[i].x(), k[i].y(), 2) for i in KeyPoint.KEY_POINT_NAMES]
        keypoints = [j for i in keypoints for j in i]
        data = {
            "info": {},
            "licenses": [],
            "images": [
                {
                    "license": 4,
                    "file_name": str(file_name),
                    #  "coco_url": "http://images.cocodataset.org/val2017/000000397133.jpg",
                    "height": self.height,
                    "width": self.width,
                    #  "date_captured": "2013-11-14 17:02:52",
                    #  "flickr_url": "http://farm7.staticflickr.com/6116/6255196340_da26cf2c9e_z.jpg",
                    "id": 0,
                },
            ],
            "annotations": [
                {
                    "segmentation": [],
                    "num_keypoints": num_keypoints,
                    "area": 5463.6864,
                    "iscrowd": 0,
                    "keypoints": keypoints,
                    "image_id": 289343,
                    "bbox": [],
                    "category_id": 1,
                    "id": 201376
                }
            ],
        }
        with file_name.open("w") as f:
            json.dump(data, f)

    def set_keypoint(self, point):
        self.keypoints[KeyPoint.KEY_POINT_NAMES[self.keypoint_index]] = point
        self.keypoint_index += 1
        self.changed = True

    def paint_keypoints(self, painter):
        color = DEFAULT_VERTEX_FILL_COLOR

        pen = QPen(color)
        pen.setWidth(max(1, int(round(2.0 / self.scale))))
        painter.setPen(pen)
        print("higehige", painter)
        # line_path = QPainterPath()
        vrtx_path = QPainterPath()
        for i in KeyPoint.KEY_POINT_NAMES:
            pen = QPen(KEY_POINT_COLORS[self.KEY_POINT_NAMES.index(i)])
            pen.setWidth(max(1, int(round(2.0 / self.scale))))
            painter.setPen(pen)
            if self.keypoints[i]:
                self.drawVertex(vrtx_path, i)

        for i in self.KEY_POINT_PAIRS:
            pen = QPen(SKELETON_COLORS[self.KEY_POINT_PAIRS.index(i)])
            pen.setWidth(max(1, int(round(2.0 / self.scale))))
            painter.setPen(pen)
            if self.keypoints[i[0]] is not None and self.keypoints[i[1]] is not None:
                painter.drawLine(self.keypoints[i[0]], self.keypoints[i[1]])

        painter.drawPath(vrtx_path)
        painter.fillPath(vrtx_path, self.vertex_fill_color)

    def reset(self):
        self.reset_keypoints()
        self.keypoint_index = 0

    def reset_keypoints(self):
        self.keypoints = {i: None for i in KeyPoint.KEY_POINT_NAMES}

    def drawVertex(self, path, i):
        d = self.point_size / self.scale
        point = self.keypoints[i]
        path.addEllipse(point, d / 2.0, d / 2.0)
