import pyrealsense2 as rs
import numpy as np
import cv2
import time
import os

# Settings
WIDTH = 424
HEIGHT = 240
FPS = 30
DURATION_SEC = 120  # 2 minutes
FRAME_COUNT = FPS * DURATION_SEC

rgb_output_dir = "rgb_frames"
depth_output_dir = "depth_frames"
os.makedirs(rgb_output_dir, exist_ok=True)
os.makedirs(depth_output_dir, exist_ok=True)

# RealSense pipeline
pipeline = rs.pipeline()
cfg = rs.config()
cfg.enable_stream(rs.stream.color, WIDTH, HEIGHT, rs.format.rgb8, FPS)
cfg.enable_stream(rs.stream.depth, WIDTH, HEIGHT, rs.format.z16, FPS)
pipeline.start(cfg)

# Warm up
for _ in range(30):
    pipeline.wait_for_frames()

print(f"Recording {DURATION_SEC} seconds ({FRAME_COUNT} frames) at {FPS} FPS...")

try:
    for frame_id in range(FRAME_COUNT):
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        depth_frame = frames.get_depth_frame()
        if not color_frame or not depth_frame:
            continue

        # Get data
        color = np.asanyarray(color_frame.get_data())  # HWC, RGB
        depth = np.asanyarray(depth_frame.get_data())  # HW, uint16

        # Save RGB as JPEG
        rgb_filename = os.path.join(rgb_output_dir, f"rgb_{frame_id:06d}.jpg")
        cv2.imwrite(rgb_filename, cv2.cvtColor(color, cv2.COLOR_RGB2BGR), [int(cv2.IMWRITE_JPEG_QUALITY), 90])

        # Save Depth as PNG (preserve 16-bit)
        depth_filename = os.path.join(depth_output_dir, f"depth_{frame_id:06d}.png")
        cv2.imwrite(depth_filename, depth)

        if frame_id % 30 == 0:
            print(f"Saved frame {frame_id}/{FRAME_COUNT}")

    print("Recording complete.")
finally:
    pipeline.stop()
