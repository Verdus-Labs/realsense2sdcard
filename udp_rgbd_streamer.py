import pyrealsense2 as rs
import numpy as np
import cv2
import socket
import struct
import time
import sys

# Settings
WIDTH, HEIGHT, FPS = 424, 240, 30
PORT = 9999

if len(sys.argv) != 2:
    print(f"Usage: python {sys.argv[0]} <receiver_ip>")
    sys.exit(1)

receiver_ip = sys.argv[1]

# UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# RealSense pipeline
pipeline = rs.pipeline()
cfg = rs.config()
cfg.enable_stream(rs.stream.color, WIDTH, HEIGHT, rs.format.rgb8, FPS)
cfg.enable_stream(rs.stream.depth, WIDTH, HEIGHT, rs.format.z16, FPS)
pipeline.start(cfg)

# Warm up
for _ in range(30):
    pipeline.wait_for_frames()

frame_id = 0
print(f"Streaming to {receiver_ip}:{PORT}")

try:
    while True:
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        depth_frame = frames.get_depth_frame()
        if not color_frame or not depth_frame:
            continue

        # Get data
        color = np.asanyarray(color_frame.get_data())  # HWC, RGB
        depth = np.asanyarray(depth_frame.get_data())  # HW, uint16

        # Compress RGB
        _, rgb_jpeg = cv2.imencode('.jpg', cv2.cvtColor(color, cv2.COLOR_RGB2BGR), [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        rgb_bytes = rgb_jpeg.tobytes()
        depth_bytes = depth.tobytes()

        # Header: frame_id(uint32), timestamp(uint64), width(uint16), height(uint16), rgb_size(uint32), depth_size(uint32)
        header = struct.pack('<I Q H H I I',
                            frame_id,
                            int(time.time() * 1e6),
                            WIDTH, HEIGHT,
                            len(rgb_bytes), len(depth_bytes))
        packet = header + rgb_bytes + depth_bytes

        if len(packet) > 65507:
            print(f"Warning: Frame {frame_id} too large for UDP packet ({len(packet)} bytes)")
            frame_id += 1
            continue

        sock.sendto(packet, (receiver_ip, PORT))
        print(f"Sent frame {frame_id} | RGB: {len(rgb_bytes)} | Depth: {len(depth_bytes)} | Total: {len(packet)} bytes")
        frame_id += 1
except KeyboardInterrupt:
    print("Stopped.")
finally:
    pipeline.stop()
    sock.close() 