#!/usr/bin/env python3

import argparse
import cv2
import json
from pyzbar.pyzbar import decode

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
    :returns: A list of JSON objects found in the QR codes in each frame
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

    # Close video file
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


def analyze_frames_data(frames_data: list) -> (int, list, list):
    """Analyze the scanned data from the QR code from each frame.

    The very first frame of the QR code video should be a sync frame, and its
    QR code should indicate how many total frames there should be in the video
    (including itself). See read_sync_frame()'s docstring on what this QR code
    data looks like.

    The rest of the frames (non-sync frames) should have 1 unique QR code each.
    Non-sync frame QR codes should indicate the frame's expected frame number
    (position) in the video.
    The data in the QR code follows a format like so:
    {
        "frame_i": <int>
    }

    This function will analyze whether there are missing frames in the video,
    and whether frames are out of order.

    :returns A tuple of (int, list, list)
               - First int returns the expected total frame count (read from
                 the sync frame). Returns 0 if there's any errors.
               - Second list returns the indices of missing frames, if any.
                 Returns an empty list if there's any errors.
               - Third list returns the indices of out of order frames, if any.
                 Returns an empty list if there's any errors.
    """
    if not frames_data:
        print("Error: no frames found in input video.")
        return 0, [], []

    # Read the frst "sync frame", which should indicate how many total expected
    # frames there should be in the video
    sync_frame_found, total_frames = read_sync_frame(frames_data)
    if not sync_frame_found:
        print("Error: first sync frame missing")
        return 0, [], []

    missing_frames = [i for i in range(1, total_frames)]
    out_of_order_frames = []

    # Go through frame by frame, starting from frame 2 (index 1)
    for i, frame in enumerate(frames_data[1:], 1):
        frame_i = frame[FRAME_I]
        # Eliminate this frame index from being considered a missing frame
        missing_frames.remove(frame_i)
        # Check if frame is out of order
        if i != frame_i:
            frame_info = {
                EXPECTED_FRAME_I: frame_i,
                ACTUAL_FRAME_I: i,
            }
            out_of_order_frames.append(frame_info)

    return total_frames, missing_frames, out_of_order_frames


def print_results(total_frames: int, missing_frames: list, out_of_order_frames: list):
    """Prints the findings made by analyze_frames_data() in a nicely formatted manner.
    """
    print(f"Expected total number of frames: {total_frames}")

    missing_frames_str = "None"
    if missing_frames:
        missing_frames_str = ", ".join([str(i) for i in missing_frames])
    print("Missing frames:")
    print(f"  {missing_frames_str}")

    out_of_order_frames_str = "None"
    print("Out-of-order frames:")
    if out_of_order_frames:
        for frame in out_of_order_frames:
            expected_i = frame[EXPECTED_FRAME_I]
            actual_i = frame[ACTUAL_FRAME_I]
            print(f"  Expected frame pos: {expected_i}, actual frame pos: {actual_i}")
    else:
        print("  None")


def parse_args():
    """Parse through program args.

    :returns the ArgumentParser object that contains program args.
    """
    parser = argparse.ArgumentParser(
            prog="QR Code Video Scanner",
            description="Scan QR codes from each QR code video frame by frame, then analyze whether the QR codes are in order")
    parser.add_argument("input_video",
                        help="Path to QR code video file")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    frames_data = scan_qr_codes(args.input_video)
    total_frames, missing_frames, out_of_order_frames = analyze_frames_data(frames_data)
    if total_frames > 0:
        print_results(total_frames, missing_frames, out_of_order_frames)
