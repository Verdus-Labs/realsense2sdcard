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

HEADER_SIZE = 21

def load_yolo():
    net = cv2.dnn.readNetFromDarknet('yolov3.cfg', 'yv3_grapes.weights')
    with open('obj.names', 'r') as f:
        classes = [line.strip() for line in f.readlines()]
    return net, classes

yolo_net, yolo_classes = load_yolo()

def detect_and_draw(frame, net, classes):
    blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    outs = net.forward(net.getUnconnectedOutLayersNames())
    height, width = frame.shape[:2]
    class_ids = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                class_ids.append(class_id)
                confidences.append(float(confidence))
                boxes.append([x, y, w, h])
    indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    for i in indices:
        i = i[0] if isinstance(i, (list, np.ndarray)) else i
        box = boxes[i]
        x, y, w, h = box
        label = classes[class_ids[i]]
        confidence = confidences[i]
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.circle(frame, ((x + int(w / 2)), (y + int(h / 2))), 5, (0, 0, 255), -1)
        cv2.putText(frame, f'{label}: {confidence:.2f}', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return frame

while True:
    packet, addr = sock.recvfrom(65536)
    if len(packet) < HEADER_SIZE:
        print("Packet too small")
        continue
    # Header: frame_id(uint32), type(uint8), timestamp(uint64), width(uint16), height(uint16), data_size(uint32)
    frame_id, typ, timestamp, width, height, data_size = struct.unpack('<IBQHHI', packet[:HEADER_SIZE])
    data = packet[HEADER_SIZE:HEADER_SIZE+data_size]
    if len(data) != data_size:
        print("Incomplete packet")
        continue
    if frame_id not in frame_buffer:
        frame_buffer[frame_id] = {}
    if typ == 0:
        # RGB (display as received, no color conversion)
        color = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
        frame_buffer[frame_id]['rgb'] = color
    elif typ == 1:
        # Depth
        depth = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_UNCHANGED)
        frame_buffer[frame_id]['depth'] = depth
    # Display if both are present and not already displayed
    if ('rgb' in frame_buffer[frame_id] and 'depth' in frame_buffer[frame_id]
        and frame_id > last_displayed):
        rgb_disp = frame_buffer[frame_id]['rgb']
        if rgb_disp is not None:
            rgb_disp = detect_and_draw(rgb_disp, yolo_net, yolo_classes)
            cv2.imshow('RGB', rgb_disp)
        d = frame_buffer[frame_id]['depth']
        if d is not None:
            # Normalize and apply heatmap
            d_norm = cv2.normalize(d, None, 255, 0, cv2.NORM_MINMAX)
            d_norm = d_norm.astype(np.uint8)
            d_heat = cv2.applyColorMap(d_norm, cv2.COLORMAP_JET)
            cv2.imshow('Depth', d_heat)
        if cv2.waitKey(1) == 27:
            break
        last_displayed = frame_id
        # Clean up old frames
        for old_id in list(frame_buffer.keys()):
            if old_id < frame_id - 10:
                del frame_buffer[old_id]
sock.close()
cv2.destroyAllWindows() 