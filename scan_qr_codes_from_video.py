#!/usr/bin/env python3

import cv2
from pyzbar.pyzbar import decode
import json

# Dictionary keys constants
TOTAL_FRAMES = "total_frames"
FRAME_I = "frame_i"
EXPECTED_FRAME_I = "expected_frame_i"
ACTUAL_FRAME_I = "actual_frame_i"

def scan_qr_codes(video_file: str):
    """Combs through a video file frame-by-frame and extracts QR codes from each frame.
    Assumes that each frame has its own 1 unique QR code.
    Returns a list of QR codes found in each frame.

    :param video_file: path to a video file to scan QR codes from (preferrably .avi files)
    :returns: A list of QR codes found in each frame
    """
    frames_data = []
    cap = cv2.VideoCapture(video_file)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        detected_qr_codes = decode(frame)
        for qr in detected_qr_codes:
            # We made the assumption that each frame would have 1 unique QR
            # code, but let's use a for loop just to be safe in case there
            # are multiple QR codes in a frame somehow
            qr_data = qr.data.decode("utf-8")
            frames_data.append(json.loads(qr_data))

    cap.release()

    return frames_data


def read_sync_frame(frames_data) -> (bool, int):
    """Checks if the contents of the QR code from very first frame in the video
    is a sync frame.
    The sync frame contains information on how many frames the QR code video
    is supposed to have.
    The sync frame should be an object in the format of:
    {
        "total_frames": <int>
    }
    Returns the supposed total number of frames if sync frame is found and
    good.

    :param frams_data: the list of all frame objects scanned from the video
    :returns A tuple containing (bool, int)
               - First bool returns True if sync frame is found and valid,
                 otherwise false
               - Second int returns the expected total number of frames in the
                 QR code video, but returns 0 if the first bool returns False
    """
    first_frame = frames_data[0]
    if TOTAL_FRAMES not in first_frame or not first_frame[TOTAL_FRAMES]:
        return False, 0
    total_frames = first_frame[TOTAL_FRAMES]
    if not isinstance(total_frames, int):
        return False, 0

    return True, first_frame[TOTAL_FRAMES]


def analyze_frames_data(frames_data: list) -> bool:
    if not frames_data:
        print("Error: no frames found in input video.")
        return False

    # Read the frst "sync frame", which should indicate how many total expected
    # frames there should be in the video
    sync_frame_found, total_frames = read_sync_frame(frames_data)
    if not sync_frame_found:
        print("Error: first sync frame missing")
        return False
    print(f"Total number of frames: {total_frames}")

    missing_frames = [i for i in range(1, total_frames)]
    out_of_order_frames = []

    # Go through frame by frame, starting from frame 2 (index 1)
    for i, frame in enumerate(frames_data[1:], 1):
        frame_i = frame[FRAME_I]
        missing_frames.remove(frame_i)
        if i != frame_i:
            ooo_info = {
                EXPECTED_FRAME_I: frame_i,
                ACTUAL_FRAME_I: i,
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
    frames_data = scan_qr_codes("qr_video.avi")
    analyze_frames_data(frames_data)
