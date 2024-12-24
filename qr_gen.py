#!/usr/bin/env python3

import cv2
import os
import qrcode
from PIL import Image
import json
import random

VID_DIMENSIONS = (500, 500)
SAVE_DIR = "qr_frames"
VIDEO_NAME = "qr_codes_out_of_order.avi"

def qr_gen(num_frames: int):
    qr_codes = []

    os.makedirs(SAVE_DIR, exist_ok=True)

    for i in range(0, num_frames):
        qr = qrcode.QRCode(version=None, box_size=10, border=5)

        qr_data = {}
        if i == 0:
            qr_data["total_frames"] = num_frames
        else:
            qr_data["frame_i"] = i
        qr.add_data(json.dumps(qr_data))

        qr.make(fit=True)
        qr_img = qr.make_image()
        qr_img = qr_img.resize(VID_DIMENSIONS, Image.ANTIALIAS)

        qr_filename = f"{SAVE_DIR}/frame{i}.png"
        qr_img.save(qr_filename)
        qr_codes.append(qr_filename)

    return qr_codes


def create_video(frame_filenames: list, fps: int):
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    video = cv2.VideoWriter(VIDEO_NAME, fourcc, fps, VID_DIMENSIONS)
    for frame_path in frame_filenames:
        frame = cv2.imread(frame_path)
        video.write(frame)
    video.release()


def shuffle_frames(qr_codes: list, num_shuffles: int):
    qr_codes_cpy = [i for i in qr_codes]

    for i in range(0, num_shuffles):
        idx1, idx2 = random.sample(range(len(qr_codes_cpy)), 2)
        print(f"idx1 = {idx1}, idx2 = {idx2}")
        qr_codes_cpy[idx1], qr_codes_cpy[idx2] = qr_codes_cpy[idx2], qr_codes_cpy[idx1]

    return qr_codes_cpy


if __name__ == "__main__":
    qr_codes = qr_gen(60)
    qr_codes = shuffle_frames(qr_codes, 6)
    create_video(qr_codes, 60)
