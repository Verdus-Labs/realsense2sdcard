# License: Apache 2.0. See LICENSE file in root directory.
# Copyright(c) 2019 Intel Corporation. All Rights Reserved.

cmake_minimum_required(VERSION 3.1.0)

project(RealsenseCapture)

# Find RealSense library
find_package(realsense2 REQUIRED)

# Add executable for one frame save
add_executable(one-frame-save one-frame-save.cpp)
set_property(TARGET one-frame-save PROPERTY CXX_STANDARD 11)
target_link_libraries(one-frame-save ${realsense2_LIBRARY})

# Add executable for 10 second capture  
add_executable(capture-10s 10s-save.cpp)
set_property(TARGET capture-10s PROPERTY CXX_STANDARD 11)
target_link_libraries(capture-10s ${realsense2_LIBRARY})

# Add executable for rpi_streamer
add_executable(rpi_streamer rpi_streamer.cpp)
set_property(TARGET rpi_streamer PROPERTY CXX_STANDARD 11)
target_link_libraries(rpi_streamer ${realsense2_LIBRARY})

# Include current directory for stb_image_write.h
include_directories(.)
