import socket
import struct
import numpy as np
import cv2

PORT = 9999

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("", PORT))

print(f"Listening on UDP port {PORT}")

while True:
    packet, addr = sock.recvfrom(65536)
    if len(packet) < 24:
        print("Packet too small")
        continue
    # Unpack header
    frame_id, timestamp, width, height, rgb_size, depth_size = struct.unpack('<I Q H H I I', packet[:24])
    rgb_start = 24
    rgb_end = rgb_start + rgb_size
    depth_start = rgb_end
    depth_end = depth_start + depth_size
    if len(packet) < depth_end:
        print("Incomplete packet")
        continue
    rgb_bytes = packet[rgb_start:rgb_end]
    depth_bytes = packet[depth_start:depth_end]
    # Decode
    color = cv2.imdecode(np.frombuffer(rgb_bytes, np.uint8), cv2.IMREAD_COLOR)
    color = cv2.cvtColor(color, cv2.COLOR_BGR2RGB)
    depth = np.frombuffer(depth_bytes, np.uint16).reshape((height, width))
    # Display
    cv2.imshow('RGB', color)
    cv2.imshow('Depth', (depth / depth.max() * 255).astype(np.uint8))
    if cv2.waitKey(1) == 27:
        break
sock.close()
cv2.destroyAllWindows() 