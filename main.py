#!/usr/bin/env python3
"""
Intel RealSense RGB-D Data Streaming to SD Card
Captures synchronized RGB and Depth streams and saves them to specified directory.
"""

import pyrealsense2 as rs
import numpy as np
import cv2
import os
import time
import signal
import sys
import json
from datetime import datetime
import threading
import argparse


class RealSenseStreamer:
    def __init__(self, output_dir="SD_CARD", width=640, height=480, fps=30):
        """
        Initialize RealSense RGB-D streamer.
        
        Args:
            output_dir (str): Path to SD card or output directory
            width (int): Frame width
            height (int): Frame height
            fps (int): Frames per second
        """
        self.output_dir = output_dir
        self.width = width
        self.height = height
        self.fps = fps
        self.frame_count = 0
        self.running = False
        
        # Create output directories
        self.rgb_dir = os.path.join(output_dir, "rgb")
        self.depth_dir = os.path.join(output_dir, "depth")
        os.makedirs(self.rgb_dir, exist_ok=True)
        os.makedirs(self.depth_dir, exist_ok=True)
        
        # Initialize RealSense pipeline
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        
        # Configure streams
        self.config.enable_stream(rs.stream.depth, width, height, rs.format.z16, fps)
        self.config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, fps)
        
        # Create alignment object (align depth to color)
        self.align = rs.align(rs.stream.color)
        
        # Metadata storage
        self.metadata = {
            "session_start": datetime.now().isoformat(),
            "resolution": f"{width}x{height}",
            "fps": fps,
            "frames": []
        }
        
        # Performance tracking
        self.last_fps_time = time.time()
        self.fps_counter = 0
        
    def start_streaming(self):
        """Start the camera pipeline and begin streaming."""
        try:
            # Start pipeline
            profile = self.pipeline.start(self.config)
            
            # Get camera intrinsics for metadata
            color_profile = profile.get_stream(rs.stream.color)
            color_intrinsics = color_profile.as_video_stream_profile().get_intrinsics()
            
            depth_profile = profile.get_stream(rs.stream.depth)
            depth_intrinsics = depth_profile.as_video_stream_profile().get_intrinsics()
            
            self.metadata["color_intrinsics"] = {
                "width": color_intrinsics.width,
                "height": color_intrinsics.height,
                "fx": color_intrinsics.fx,
                "fy": color_intrinsics.fy,
                "ppx": color_intrinsics.ppx,
                "ppy": color_intrinsics.ppy
            }
            
            self.metadata["depth_intrinsics"] = {
                "width": depth_intrinsics.width,
                "height": depth_intrinsics.height,
                "fx": depth_intrinsics.fx,
                "fy": depth_intrinsics.fy,
                "ppx": depth_intrinsics.ppx,
                "ppy": depth_intrinsics.ppy
            }
            
            print(f"Started RealSense streaming at {self.width}x{self.height}@{self.fps}fps")
            print(f"Output directory: {self.output_dir}")
            print("Press Ctrl+C to stop streaming...")
            
            self.running = True
            self.stream_loop()
            
        except Exception as e:
            print(f"Error starting camera: {e}")
            sys.exit(1)
    
    def stream_loop(self):
        """Main streaming loop."""
        try:
            while self.running:
                # Wait for frames
                frames = self.pipeline.wait_for_frames()
                
                # Align depth frame to color frame
                aligned_frames = self.align.process(frames)
                
                # Get aligned frames
                color_frame = aligned_frames.get_color_frame()
                depth_frame = aligned_frames.get_depth_frame()
                
                if not color_frame or not depth_frame:
                    continue
                
                # Get frame data
                color_image = np.asanyarray(color_frame.get_data())
                depth_image = np.asanyarray(depth_frame.get_data())
                
                # Get timestamp
                timestamp = int(time.time() * 1000)  # milliseconds
                
                # Save frames in separate thread to avoid blocking
                threading.Thread(
                    target=self.save_frames,
                    args=(color_image, depth_image, timestamp),
                    daemon=True
                ).start()
                
                self.frame_count += 1
                self.fps_counter += 1
                
                # Update FPS display
                current_time = time.time()
                if current_time - self.last_fps_time >= 1.0:
                    print(f"FPS: {self.fps_counter:.1f} | Frames saved: {self.frame_count}")
                    self.fps_counter = 0
                    self.last_fps_time = current_time
                
        except KeyboardInterrupt:
            print("\nStopping stream...")
        except Exception as e:
            print(f"Error during streaming: {e}")
        finally:
            self.stop_streaming()
    
    def save_frames(self, color_image, depth_image, timestamp):
        """Save RGB and depth frames to disk."""
        try:
            # Create filenames
            filename_base = f"frame_{self.frame_count:06d}_{timestamp}"
            rgb_filename = os.path.join(self.rgb_dir, f"{filename_base}.jpg")
            depth_filename = os.path.join(self.depth_dir, f"{filename_base}.png")
            
            # Save RGB frame as JPEG
            cv2.imwrite(rgb_filename, color_image, [cv2.IMWRITE_JPEG_QUALITY, 90])
            
            # Save depth frame as 16-bit PNG
            cv2.imwrite(depth_filename, depth_image)
            
            # Update metadata
            frame_info = {
                "frame_number": self.frame_count,
                "timestamp": timestamp,
                "rgb_file": f"rgb/{filename_base}.jpg",
                "depth_file": f"depth/{filename_base}.png"
            }
            self.metadata["frames"].append(frame_info)
            
        except Exception as e:
            print(f"Error saving frame {self.frame_count}: {e}")
    
    def stop_streaming(self):
        """Stop streaming and cleanup."""
        self.running = False
        
        # Stop pipeline
        if hasattr(self, 'pipeline'):
            self.pipeline.stop()
        
        # Save metadata
        self.metadata["session_end"] = datetime.now().isoformat()
        self.metadata["total_frames"] = self.frame_count
        
        metadata_file = os.path.join(self.output_dir, "metadata.json")
        try:
            with open(metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
            print(f"Session metadata saved to: {metadata_file}")
        except Exception as e:
            print(f"Error saving metadata: {e}")
        
        print(f"Streaming stopped. Total frames captured: {self.frame_count}")


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print("\nReceived interrupt signal...")
    sys.exit(0)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Intel RealSense RGB-D Streamer")
    parser.add_argument("--output", "-o", default="SD_CARD",
                        help="Output directory (SD card folder)")
    parser.add_argument("--width", "-w", type=int, default=640,
                        help="Frame width (default: 640)")
    parser.add_argument("--height", "-ht", type=int, default=480,
                        help="Frame height (default: 480)")
    parser.add_argument("--fps", "-f", type=int, default=30,
                        help="Frames per second (default: 30)")
    
    args = parser.parse_args()
    
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create output directory if it doesn't exist
    if not os.path.exists(args.output):
        try:
            os.makedirs(args.output, exist_ok=True)
            print(f"Created output directory: {args.output}")
        except Exception as e:
            print(f"Error creating output directory '{args.output}': {e}")
            sys.exit(1)
    
    # Create and start streamer
    streamer = RealSenseStreamer(
        output_dir=args.output,
        width=args.width,
        height=args.height,
        fps=args.fps
    )
    
    try:
        streamer.start_streaming()
    except KeyboardInterrupt:
        streamer.stop_streaming()


if __name__ == "__main__":
    main() 