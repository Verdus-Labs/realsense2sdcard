import socket
import struct
import numpy as np
import cv2
import time

PORT = 9999
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("", PORT))

print(f"Listening on UDP port {PORT}")

frame_buffer = {}
last_displayed = -1

while True:
    packet, addr = sock.recvfrom(65536)
    if len(packet) < 19:
        print("Packet too small")
        continue
    # Header: frame_id(uint32), type(uint8), timestamp(uint64), width(uint16), height(uint16), data_size(uint32)
    frame_id, typ, timestamp, width, height, data_size = struct.unpack('<IBQHHI', packet[:19])
    data = packet[19:19+data_size]
    if len(data) != data_size:
        print("Incomplete packet")
        continue
    if frame_id not in frame_buffer:
        frame_buffer[frame_id] = {}
    if typ == 0:
        # RGB
        color = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
        if color is not None:
            color = cv2.cvtColor(color, cv2.COLOR_BGR2RGB)
        frame_buffer[frame_id]['rgb'] = color
    elif typ == 1:
        # Depth
        depth = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_UNCHANGED)
        frame_buffer[frame_id]['depth'] = depth
    # Display if both are present and not already displayed
    if ('rgb' in frame_buffer[frame_id] and 'depth' in frame_buffer[frame_id]
        and frame_id > last_displayed):
        cv2.imshow('RGB', frame_buffer[frame_id]['rgb'])
        d = frame_buffer[frame_id]['depth']
        if d is not None:
            d_show = (d / d.max() * 255).astype(np.uint8) if d.max() > 0 else d.astype(np.uint8)
            cv2.imshow('Depth', d_show)
        if cv2.waitKey(1) == 27:
            break
        last_displayed = frame_id
        # Clean up old frames
        for old_id in list(frame_buffer.keys()):
            if old_id < frame_id - 10:
                del frame_buffer[old_id]
sock.close()
cv2.destroyAllWindows() 