# Intel RealSense RGB-D Streaming to SD Card

A Python program that captures synchronized RGB and Depth data from Intel RealSense cameras and streams it directly to an SD card or storage device.

## Features

- **Real-time RGB-D capture**: Synchronized color and depth streams
- **Efficient storage**: Saves RGB as JPEG and depth as 16-bit PNG
- **Metadata tracking**: Complete session metadata with camera intrinsics
- **Performance monitoring**: Real-time FPS display and frame counting
- **Configurable parameters**: Resolution, frame rate, and output location
- **Graceful shutdown**: Proper cleanup on interruption

## Requirements

- Intel RealSense camera (D400 series recommended)
- Python 3.7+
- SD card or external storage device

## Installation

### 1. Install Basic Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install Intel RealSense SDK

#### **Raspberry Pi** (Recommended Method)
```bash
# Install librealsense2 system package
sudo apt update
sudo apt install -y librealsense2-dev librealsense2-utils

# Install Python bindings
pip install pyrealsense2

# If pip install fails, try building from source:
# git clone https://github.com/IntelRealSense/librealsense.git
# cd librealsense && mkdir build && cd build
# cmake .. -DBUILD_PYTHON_BINDINGS=bool:true -DPYTHON_EXECUTABLE=$(which python3)
# make -j4 && sudo make install
```

#### **Other Platforms**
- **macOS**: `brew install librealsense`
- **Ubuntu**: Follow [official installation guide](https://github.com/IntelRealSense/librealsense/blob/master/doc/distribution_linux.md)
- **Windows**: Download from [Intel's website](https://www.intelrealsense.com/sdk-2/)

#### **Alternative: Install via pip** (most systems except RPi)
```bash
pip install pyrealsense2>=2.54.1
```

## Usage

### 1. Test Camera Setup

First, verify your camera is working:

```bash
python test_camera.py
```

This will:
- List all connected RealSense devices
- Show available stream configurations
- Test basic streaming functionality

### 2. Start RGB-D Streaming

**Basic usage** (saves to `SD_CARD/` folder in current directory):
```bash
python main.py
```

**Specify custom output directory:**
```bash
python main.py --output /path/to/custom_folder
```

**Custom resolution and frame rate:**
```bash
python main.py --width 848 --height 480 --fps 60 --output MY_DATA
```

### 3. Stop Streaming

Press `Ctrl+C` to stop streaming. The program will:
- Gracefully stop the camera pipeline
- Save session metadata to `metadata.json`
- Display total frames captured

## Command Line Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--output` | `-o` | `SD_CARD` | Output directory (will be created if not exists) |
| `--width` | `-w` | `640` | Frame width in pixels |
| `--height` | `-ht` | `480` | Frame height in pixels |
| `--fps` | `-f` | `30` | Frames per second |

## Output Structure

The program creates the following directory structure:

```
OUTPUT_DIR/
├── rgb/
│   ├── frame_000001_1234567890.jpg
│   ├── frame_000002_1234567891.jpg
│   └── ...
├── depth/
│   ├── frame_000001_1234567890.png
│   ├── frame_000002_1234567891.png
│   └── ...
└── metadata.json
```

### File Naming Convention

- **RGB files**: `frame_{frame_number:06d}_{timestamp}.jpg`
- **Depth files**: `frame_{frame_number:06d}_{timestamp}.png`
- **Timestamp**: Milliseconds since epoch for synchronization

### Metadata Format

The `metadata.json` file contains:

```json
{
  "session_start": "2024-01-01T12:00:00.000Z",
  "session_end": "2024-01-01T12:05:00.000Z",
  "resolution": "640x480",
  "fps": 30,
  "total_frames": 9000,
  "color_intrinsics": {
    "width": 640,
    "height": 480,
    "fx": 617.315,
    "fy": 617.315,
    "ppx": 320.0,
    "ppy": 240.0
  },
  "depth_intrinsics": { ... },
  "frames": [
    {
      "frame_number": 1,
      "timestamp": 1234567890,
      "rgb_file": "rgb/frame_000001_1234567890.jpg",
      "depth_file": "depth/frame_000001_1234567890.png"
    }
  ]
}
```

## Performance Tips

1. **Use fast SD cards**: Class 10 or UHS-I/II for best performance
2. **Lower resolution**: Use 640x480 for longer recording sessions
3. **Monitor storage**: Check available space before long captures
4. **USB 3.0**: Ensure camera is connected to USB 3.0+ port

## Troubleshooting

### "No RealSense devices found"
- Check USB connection
- Try different USB port (preferably USB 3.0)
- Run `python test_camera.py` to diagnose

### "Permission denied" errors
- Ensure SD card is writable
- Check available disk space
- Verify mount permissions

### Low FPS or frame drops
- Reduce resolution or frame rate
- Use faster storage device
- Close other applications using camera

### "Pipeline failed to start"
- Camera may be in use by another application
- Try different resolution/format combination
- Restart camera or reconnect USB

## Supported Camera Models

- Intel RealSense D415
- Intel RealSense D435
- Intel RealSense D435i
- Intel RealSense D455
- Other D400 series cameras

## Technical Details

- **RGB format**: BGR8 (OpenCV compatible)
- **Depth format**: 16-bit unsigned integer (millimeters)
- **Alignment**: Depth frames aligned to color frame coordinates
- **Threading**: Asynchronous file I/O to maintain real-time performance
- **Compression**: JPEG quality 90% for RGB, lossless PNG for depth

## License

This project is provided as-is for educational and research purposes. 