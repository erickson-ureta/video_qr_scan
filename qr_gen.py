#!/usr/bin/env python3

import argparse
import cv2
import os
import qrcode
from PIL import Image
import json
import random
import sys

VID_DIMENSIONS = (500, 500)
SAVE_DIR = "qr_frames"

def generate_qr_codes(num_frames: int):
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


def create_video(output_path: str, frame_filenames: list, fps: int):
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    video = cv2.VideoWriter(output_path, fourcc, fps, VID_DIMENSIONS)
    for frame_path in frame_filenames:
        frame = cv2.imread(frame_path)
        video.write(frame)
    video.release()


def random_shuffle_frames(qr_codes: list, num_shuffles: int):
    qr_codes_cpy = [i for i in qr_codes]
    for i in range(0, num_shuffles):
        idx1, idx2 = random.sample(range(len(qr_codes_cpy)), 2)
        print(f"Switching frames {idx1} and {idx2}")
        qr_codes_cpy[idx1], qr_codes_cpy[idx2] = qr_codes_cpy[idx2], qr_codes_cpy[idx1]

    return qr_codes_cpy


def parse_args():
    parser = argparse.ArgumentParser(
            prog="QR Code Video Generator",
            description="Create a small video that contains QR codes per frame")
    parser.add_argument("num_frames",
                        type=int,
                        help="Total number of frames that the resulting video should have")
    parser.add_argument("output_path",
                        type=str,
                        help="Path where to save the resulting output video")
    parser.add_argument("--scramble", "-s",
                        type=int,
                        help="Swaps frames around up to the specified amount. Must not be greater than the specified num_frames")

    args = parser.parse_args()
    if args.num_frames <= 0:
        print("Error: num_frames must be a value above 0")
        return None
    if args.scramble and (args.scramble < 0 or args.scramble > args.num_frames):
        print("Error: scramble must be a value between 0 and specified num_frames")
        return None

    return args


if __name__ == "__main__":
    args = parse_args()
    if not args:
        sys.exit(1)
    qr_codes = generate_qr_codes(args.num_frames)
    #qr_codes = random_shuffle_frames(qr_codes, 6)
    create_video(args.output_path, qr_codes, 60)
