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
DEFAULT_OUTPUT_FILE = "qr_video.avi"

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
    print(f"QR video file successfully written to: {output_path}")


def random_shuffle_frames(qr_codes: list, num_shuffles: int):
    qr_codes_cpy = [i for i in qr_codes]
    for i in range(0, num_shuffles):
        idx1, idx2 = random.sample(range(1, len(qr_codes_cpy)), 2)
        print(f"Switching frames {idx1} and {idx2}")
        qr_codes_cpy[idx1], qr_codes_cpy[idx2] = qr_codes_cpy[idx2], qr_codes_cpy[idx1]

    return qr_codes_cpy


def random_delete_frames(qr_codes: list, num_deletes: int):
    random_qr_codes_to_delete = set(random.sample(range(len(qr_codes)), num_deletes))
    print(f"Deleted frames: {random_qr_codes_to_delete}")

    return [qr for i, qr in enumerate(qr_codes) if i not in random_qr_codes_to_delete]


def parse_args():
    parser = argparse.ArgumentParser(
            prog="QR Code Video Generator",
            description="Create a small video that contains QR codes per frame")
    parser.add_argument("num_frames",
                        type=int,
                        help="Total number of frames that the resulting video should have")
    parser.add_argument("--output_path", "-o",
                        type=str,
                        help="Path where to save the resulting output video")
    parser.add_argument("--scramble", "-s",
                        type=int,
                        help="Swaps frames around up to the specified amount of times")
    parser.add_argument("--delete_random", "-d",
                        type=int,
                        help="Randomly deletes frames around up to the specified amount. Must not be greater than the specified num_frames")

    args = parser.parse_args()
    if args.output_path and len(args.output_path) <= 0:
        print("Error: output_path must not be empty")
        return None
    if args.num_frames <= 0:
        print("Error: num_frames must be a value above 0")
        return None
    if args.scramble and args.scramble < 0:
        print("Error: scramble must be a value above 0")
        return None
    if args.delete_random and (args.delete_random < 0 or args.delete_random > args.num_frames):
        print("Error: delete_random must be a value between 1 and the specified num_frames value")
        return None

    return args


if __name__ == "__main__":
    args = parse_args()
    if not args:
        sys.exit(1)

    qr_codes = generate_qr_codes(args.num_frames)
    if args.scramble:
        qr_codes = random_shuffle_frames(qr_codes, args.scramble)
    if args.delete_random:
        qr_codes = random_delete_frames(qr_codes, args.delete_random)

    output_path = DEFAULT_OUTPUT_FILE if not args.output_path else args.output_path
    create_video(output_path, qr_codes, 60)
