#!/usr/bin/env python3

import cv2
from pyzbar.pyzbar import decode
import json

TOTAL_FRAMES = "total_frames"
FRAME_I = "frame_i"
EXPECTED_FRAME_I = "expected_frame_i"
ACTUAL_FRAME_I = "actual_frame_i"

def scan_qr_codes(video_file: str):
    frames_data = []
    cap = cv2.VideoCapture(video_file)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        detected_qr_codes = decode(frame)
        for qr in detected_qr_codes:
            qr_data = qr.data.decode("utf-8")
            frames_data.append(json.loads(qr_data))

    cap.release()

    return frames_data


def _read_sync_frame(sync_frame) -> (bool, int):
    if TOTAL_FRAMES not in frames_data[0] or not frames_data[0][TOTAL_FRAMES]:
        return False, 0
    return True, frames_data[0][TOTAL_FRAMES]


def verify_frames_data(frames_data: list) -> bool:
    if not frames_data:
        print("Error: no frames found in input video.")
        return False

    # Read the frst "sync frame", which should indicate how many total expected
    # frames there should be in the video
    sync_frame_found, total_frames = _read_sync_frame(frames_data[0])
    if not sync_frame_found:
        print("Error: first sync frame missing")
        return False
    print(f"Total number of frames: {total_frames}")

    missing_frames = [i for i in range(1, total_frames)]
    out_of_order_frames = []

    # Go through frame by frame
    for i, frame in enumerate(frames_data[1:]):
        frame_i = frame[FRAME_I]
        missing_frames.remove(frame_i)
        if i != frame_i:
            ooo_info = {
                EXPECTED_FRAME_I: i,
                ACTUAL_FRAME_I: frame_i,
            }
            out_of_order_frames.append(ooo_info)

    if not missing_frames:
        print(f"Missing frames: None")
    else:
        print("Missing frames:")
        print(",".join([str(i) for i in missing_frames]))
    if not out_of_order_frames:
        print("Out of order frames: None")
    else:
        print("Out of order frames:")
        for ooof in out_of_order_frames:
            expected_i = ooof[EXPECTED_FRAME_I]
            actual_i = ooof[ACTUAL_FRAME_I]
            print(f"  Expected frame pos: {expected_i}, actual frame pos: {actual_i}")

    return True

if __name__ == "__main__":
    frames_data = scan_qr_codes("qr_codes.avi")
    #frames_data = scan_qr_codes("qr_codes_out_of_order.avi")
    verify_frames_data(frames_data)
