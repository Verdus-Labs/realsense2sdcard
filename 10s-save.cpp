// License: Apache 2.0. See LICENSE file in root directory.
// Copyright(c) 2015-2017 Intel Corporation. All Rights Reserved.

#include <librealsense2/rs.hpp> // Include RealSense Cross Platform API

#include <fstream>              // File IO
#include <iostream>             // Terminal IO
#include <sstream>              // Stringstreams
#include <chrono>               // Time handling
#include <iomanip>              // For formatting
#include <sys/stat.h>           // For directory creation

// 3rd party header for writing png files
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"

// Helper function for writing metadata to disk as a csv file
void metadata_to_csv(const rs2::frame& frm, const std::string& filename);

// Helper function to create timestamped filename
std::string create_filename(const std::string& base_dir, const std::string& stream_name, 
                           int frame_number, long long timestamp, const std::string& extension);

// Helper function to create directory
void create_directory(const std::string& path);

// This sample captures 10 seconds of footage and saves all frames to disk
int main(int argc, char * argv[]) try
{
    // Create captured_data directory structure
    create_directory("captured_data");
    create_directory("captured_data/rgb");
    create_directory("captured_data/depth");
    create_directory("captured_data/metadata");

    // Declare depth colorizer for pretty visualization of depth data
    rs2::colorizer color_map;

    // Declare RealSense pipeline, encapsulating the actual device and sensors
    rs2::pipeline pipe;
    
    // Configure pipeline for specific streams
    rs2::config cfg;
    cfg.enable_stream(RS2_STREAM_COLOR, 640, 480, RS2_FORMAT_BGR8, 30);
    cfg.enable_stream(RS2_STREAM_DEPTH, 640, 480, RS2_FORMAT_Z16, 30);
    
    // Start streaming with configuration
    pipe.start(cfg);

    std::cout << "🔧 Starting RealSense pipeline..." << std::endl;

    // Capture 30 frames to give autoexposure, etc. a chance to settle
    std::cout << "⏳ Stabilizing camera (30 frames)..." << std::endl;
    for (auto i = 0; i < 30; ++i) {
        pipe.wait_for_frames();
        std::cout << "\rStabilizing... " << (i+1) << "/30" << std::flush;
    }
    std::cout << std::endl;

    // Record start time
    auto start_time = std::chrono::high_resolution_clock::now();
    auto capture_duration = std::chrono::seconds(10);  // 10 seconds
    
    int frame_count = 0;
    std::cout << "🎬 Starting 10-second capture..." << std::endl;
    std::cout << "📁 Saving to captured_data/ folder" << std::endl;

    // Main capture loop - run for 10 seconds
    while (true) {
        auto current_time = std::chrono::high_resolution_clock::now();
        auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(current_time - start_time);
        
        // Check if 10 seconds have passed
        if (elapsed >= capture_duration) {
            break;
        }

        // Get timestamp in milliseconds
        long long timestamp = std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();

        // Wait for the next set of frames from the camera
        rs2::frameset frames = pipe.wait_for_frames();
        frame_count++;

        // Process each frame in the frameset
        for (auto&& frame : frames) {
            // We can only save video frames as pngs, so we skip the rest
            if (auto vf = frame.as<rs2::video_frame>()) {
                auto stream = frame.get_profile().stream_type();
                
                // Handle different stream types
                if (stream == RS2_STREAM_COLOR) {
                    // Save RGB frame
                    std::string rgb_filename = create_filename("captured_data/rgb", "color", frame_count, timestamp, ".png");
                    stbi_write_png(rgb_filename.c_str(), vf.get_width(), vf.get_height(),
                                   vf.get_bytes_per_pixel(), vf.get_data(), vf.get_stride_in_bytes());
                    
                    // Save RGB metadata
                    std::string rgb_meta_filename = create_filename("captured_data/metadata", "color", frame_count, timestamp, "_metadata.csv");
                    metadata_to_csv(vf, rgb_meta_filename);
                    
                } else if (stream == RS2_STREAM_DEPTH) {
                    // Save raw depth frame (16-bit)
                    std::string depth_filename = create_filename("captured_data/depth", "depth", frame_count, timestamp, ".png");
                    stbi_write_png(depth_filename.c_str(), vf.get_width(), vf.get_height(),
                                   vf.get_bytes_per_pixel(), vf.get_data(), vf.get_stride_in_bytes());
                    
                    // Save colorized depth for visualization
                    auto colorized_depth = color_map.process(frame);
                    std::string depth_color_filename = create_filename("captured_data/depth", "depth_colorized", frame_count, timestamp, ".png");
                    stbi_write_png(depth_color_filename.c_str(), colorized_depth.get_width(), colorized_depth.get_height(),
                                   colorized_depth.get_bytes_per_pixel(), colorized_depth.get_data(), colorized_depth.get_stride_in_bytes());
                    
                    // Save depth metadata
                    std::string depth_meta_filename = create_filename("captured_data/metadata", "depth", frame_count, timestamp, "_metadata.csv");
                    metadata_to_csv(vf, depth_meta_filename);
                }
            }
        }

        // Progress update every 30 frames (~1 second at 30fps)
        if (frame_count % 30 == 0) {
            float seconds_elapsed = elapsed.count() / 1000.0f;
            std::cout << "\r📸 Frame " << frame_count << " | " << std::fixed << std::setprecision(1) 
                      << seconds_elapsed << "s / 10.0s" << std::flush;
        }
    }

    std::cout << std::endl << "✅ Capture complete!" << std::endl;
    std::cout << "📊 Total frames captured: " << frame_count << std::endl;
    std::cout << "📁 Files saved to captured_data/ folder" << std::endl;
    std::cout << "   - captured_data/rgb/ (color frames)" << std::endl;
    std::cout << "   - captured_data/depth/ (depth frames + colorized)" << std::endl;
    std::cout << "   - captured_data/metadata/ (frame metadata)" << std::endl;

    return EXIT_SUCCESS;
}
catch(const rs2::error & e)
{
    std::cerr << "RealSense error calling " << e.get_failed_function() << "(" << e.get_failed_args() << "):\n    " << e.what() << std::endl;
    return EXIT_FAILURE;
}
catch(const std::exception & e)
{
    std::cerr << e.what() << std::endl;
    return EXIT_FAILURE;
}

std::string create_filename(const std::string& base_dir, const std::string& stream_name, 
                           int frame_number, long long timestamp, const std::string& extension)
{
    std::stringstream filename;
    filename << base_dir << "/frame_" << std::setfill('0') << std::setw(6) << frame_number 
             << "_" << timestamp << "_" << stream_name << extension;
    return filename.str();
}

void create_directory(const std::string& path) {
    struct stat info;
    if (stat(path.c_str(), &info) != 0) {
        // Directory doesn't exist, create it
#ifdef _WIN32
        _mkdir(path.c_str());
#else
        mkdir(path.c_str(), 0755);
#endif
    }
}

void metadata_to_csv(const rs2::frame& frm, const std::string& filename)
{
    std::ofstream csv;
    csv.open(filename);

    csv << "Stream," << rs2_stream_to_string(frm.get_profile().stream_type()) << "\nMetadata Attribute,Value\n";

    // Record all the available metadata attributes
    for (size_t i = 0; i < RS2_FRAME_METADATA_COUNT; i++)
    {
        if (frm.supports_frame_metadata((rs2_frame_metadata_value)i))
        {
            csv << rs2_frame_metadata_to_string((rs2_frame_metadata_value)i) << ","
                << frm.get_frame_metadata((rs2_frame_metadata_value)i) << "\n";
        }
    }

    csv.close();
}