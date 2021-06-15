#!/usr/bin/env python
# -*- coding: utf8 -*-
import json
from libs.keypoint import KeyPoint
from pathlib import Path
from typing import List
from PyQt5.QtCore import QPoint
from libs.constants import DEFAULT_ENCODING
import os

JSON_EXT = '.json'
ENCODE_METHOD = DEFAULT_ENCODING


class CreateMLWriter:
    def __init__(self, folder_name, filename, img_size, shapes, keypoints: List[KeyPoint], output_file: Path, database_src='Unknown', local_img_path=None):
        self.folder_name = folder_name
        self.filename = filename
        self.database_src = database_src
        self.img_size = img_size
        self.box_list = []
        self.local_img_path = local_img_path
        self.verified = False
        self.shapes = shapes
        self.keypoints = keypoints
        self.output_file = output_file

    def write(self):
        if self.output_file.is_file():
            with self.output_file.open() as f:
                output_dict = json.load(f)
        else:
            output_dict = []

        output_image_dict = {
            "image": self.filename,
            "annotations": [],
            "keypoints": [],
        }

        for shape in self.shapes:
            points = shape["points"]

            x1 = points[0][0]
            y1 = points[0][1]
            x2 = points[1][0]
            y2 = points[2][1]

            height, width, x, y = self.calculate_coordinates(x1, x2, y1, y2)

            shape_dict = {
                "label": shape["label"],
                "coordinates": {
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height
                }
            }
            output_image_dict["annotations"].append(shape_dict)

        zero = (0, 0, 0)
        for keypiont_obj in self.keypoints:
            k = keypiont_obj.keypoints
            keypoints = [zero if k[i] is None else (k[i].x(), k[i].y(), 2) for i in KeyPoint.KEY_POINT_NAMES]
            output_image_dict["keypoints"].append(keypoints)
            # keypoints = [j for i in keypoints for j in i]

        # check if image already in output
        exists = False
        for i in range(0, len(output_dict)):
            if output_dict[i]["image"] == output_image_dict["image"]:
                exists = True
                output_dict[i] = output_image_dict
                break

        if not exists:
            output_dict.append(output_image_dict)
        with self.output_file.open("w") as f:
            json.dump(output_dict, f, indent=4, sort_keys=True, separators=(',', ': '))
        # Path(self.output_file).write_text(json.dumps(output_dict), ENCODE_METHOD)

    def calculate_coordinates(self, x1, x2, y1, y2):
        if x1 < x2:
            x_min = x1
            x_max = x2
        else:
            x_min = x2
            x_max = x1
        if y1 < y2:
            y_min = y1
            y_max = y2
        else:
            y_min = y2
            y_max = y1
        width = x_max - x_min
        if width < 0:
            width = width * -1
        height = y_max - y_min
        # x and y from center of rect
        x = x_min + width / 2
        y = y_min + height / 2
        return height, width, x, y


class CreateMLReader:
    def __init__(self, json_path: Path, file_path: Path):
        self.json_path = json_path
        self.shapes = []
        self.keypoints = []
        self.verified = False
        self.filename = file_path.name
        try:
            self.parse_json()
        except ValueError:
            print("JSON decoding failed")

    def parse_json(self):
        with self.json_path.open() as f:
            output_dict = json.load(f)
        self.verified = True
        self.shapes = []
        self.keypoints = []

        keypoint_num = len(KeyPoint.KEY_POINT_NAMES)
        for image in output_dict:
            if image["image"] == self.filename:
                for shape in image["annotations"]:
                    self.add_shape(shape["label"], shape["coordinates"])

                for keypoint in image["keypoints"]:
                    keypoint_obj = KeyPoint()
                    assert len(keypoint) == keypoint_num
                    for i, name in enumerate(KeyPoint.KEY_POINT_NAMES):
                        if keypoint[i][2]:
                            keypoint_obj.keypoints[name] = QPoint(keypoint[i][0], keypoint[i][1])
                    self.keypoints.append(keypoint_obj)

    def add_shape(self, label, bnd_box):
        x_min = bnd_box["x"] - (bnd_box["width"] / 2)
        y_min = bnd_box["y"] - (bnd_box["height"] / 2)

        x_max = bnd_box["x"] + (bnd_box["width"] / 2)
        y_max = bnd_box["y"] + (bnd_box["height"] / 2)

        points = [(x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max)]
        self.shapes.append((label, points, None, None, True))

    def get_shapes(self):
        return self.shapes
