#!/usr/bin/env python3
"""
Test script to verify Intel RealSense camera connectivity and configurations.
"""

import pyrealsense2 as rs
import sys


def list_devices():
    """List all connected RealSense devices."""
    ctx = rs.context()
    devices = ctx.query_devices()
    
    if len(devices) == 0:
        print("No RealSense devices found!")
        return False
    
    print(f"Found {len(devices)} RealSense device(s):")
    
    for i, device in enumerate(devices):
        print(f"\nDevice {i}:")
        print(f"  Name: {device.get_info(rs.camera_info.name)}")
        print(f"  Serial: {device.get_info(rs.camera_info.serial_number)}")
        print(f"  Firmware: {device.get_info(rs.camera_info.firmware_version)}")
        
        # List available sensors
        sensors = device.query_sensors()
        print(f"  Sensors: {len(sensors)}")
        
        for j, sensor in enumerate(sensors):
            print(f"    Sensor {j}: {sensor.get_info(rs.camera_info.name)}")
            
            # List available stream profiles
            profiles = sensor.get_stream_profiles()
            for profile in profiles:
                if profile.is_video_stream_profile():
                    vp = profile.as_video_stream_profile()
                    print(f"      {vp.stream_type()}: {vp.width()}x{vp.height()} @ {vp.fps()}fps, {vp.format()}")
    
    return True


def test_streaming():
    """Test basic streaming functionality."""
    print("\nTesting basic streaming...")
    
    pipeline = rs.pipeline()
    config = rs.config()
    
    # Configure streams
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    
    try:
        # Start pipeline
        pipeline.start(config)
        print("✓ Pipeline started successfully")
        
        # Try to get a few frames
        for i in range(5):
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            depth_frame = frames.get_depth_frame()
            
            if color_frame and depth_frame:
                print(f"✓ Frame {i+1}: RGB and Depth frames captured")
            else:
                print(f"✗ Frame {i+1}: Missing frames")
        
        pipeline.stop()
        print("✓ Streaming test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Streaming test failed: {e}")
        return False


def main():
    """Main test function."""
    print("Intel RealSense Camera Test")
    print("=" * 40)
    
    # Test device detection
    if not list_devices():
        print("\nPlease connect a RealSense camera and try again.")
        sys.exit(1)
    
    # Test streaming
    if test_streaming():
        print("\n✓ Camera is ready for RGB-D streaming!")
        print("\nYou can now run the main streaming program:")
        print("python main.py  # (saves to SD_CARD/ folder)")
        print("python main.py --output /path/to/custom_folder")
    else:
        print("\n✗ Camera streaming test failed.")
        print("Please check camera connection and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main() 