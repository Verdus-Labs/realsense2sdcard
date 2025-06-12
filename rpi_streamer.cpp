// rpi_streamer.cpp - Network streaming version
#include <librealsense2/rs.hpp>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <iostream>
#include <chrono>
#include <cstring>
#include <thread>

// Network frame structure
struct NetworkFrame {
    uint32_t frame_id;
    uint64_t timestamp;
    uint16_t width, height;
    uint32_t rgb_size;
    uint32_t depth_size;
    // Followed by: RGB data + Depth data
};

// Simple JPEG compression using librealsense built-in
std::vector<uint8_t> compress_rgb(const rs2::video_frame& frame) {
    // For now, we'll send raw RGB - you can add JPEG compression here
    const uint8_t* data = (const uint8_t*)frame.get_data();
    size_t size = frame.get_data_size();
    return std::vector<uint8_t>(data, data + size);
}

int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cout << "Usage: ./rpi_streamer <computer_ip>" << std::endl;
        return -1;
    }
    
    const char* computer_ip = argv[1];
    const int port = 9999;
    
    // Create UDP socket
    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        perror("socket");
        return -1;
    }
    
    // Set socket to non-blocking and increase buffer size
    int buffer_size = 1024 * 1024; // 1MB buffer
    setsockopt(sock, SOL_SOCKET, SO_SNDBUF, &buffer_size, sizeof(buffer_size));
    
    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    inet_pton(AF_INET, computer_ip, &server_addr.sin_addr);
    
    // Configure RealSense
    rs2::pipeline pipe;
    rs2::config cfg;
    
    // Moderate resolution for network streaming
    cfg.enable_stream(RS2_STREAM_COLOR, 424, 240, RS2_FORMAT_RGB8, 30);
    cfg.enable_stream(RS2_STREAM_DEPTH, 424, 240, RS2_FORMAT_Z16, 30);
    
    try {
        pipe.start(cfg);
        std::cout << "RealSense started - streaming to " << computer_ip << ":" << port << std::endl;
        
        // Stabilization
        for (int i = 0; i < 30; ++i) pipe.wait_for_frames();
        
        uint32_t frame_count = 0;
        auto last_fps_time = std::chrono::steady_clock::now();
        int fps_counter = 0;
        
        while (true) {
            auto frames = pipe.wait_for_frames();
            auto color = frames.get_color_frame();
            auto depth = frames.get_depth_frame();
            
            if (!color || !depth) continue;
            
            // Prepare network frame
            NetworkFrame header;
            header.frame_id = frame_count++;
            header.timestamp = std::chrono::high_resolution_clock::now()
                              .time_since_epoch().count();
            header.width = color.get_width();
            header.height = color.get_height();
            header.rgb_size = color.get_data_size();
            header.depth_size = depth.get_data_size();
            
            // Create packet: header + rgb + depth
            size_t total_size = sizeof(NetworkFrame) + header.rgb_size + header.depth_size;
            std::vector<uint8_t> packet(total_size);
            
            // Copy header
            memcpy(packet.data(), &header, sizeof(NetworkFrame));
            
            // Copy RGB data
            memcpy(packet.data() + sizeof(NetworkFrame), 
                   color.get_data(), header.rgb_size);
            
            // Copy depth data
            memcpy(packet.data() + sizeof(NetworkFrame) + header.rgb_size,
                   depth.get_data(), header.depth_size);
            
            // Send packet (may need to split for large frames)
            if (total_size > 65507) { // UDP max payload
                std::cout << "Warning: Frame too large for single UDP packet" << std::endl;
                continue;
            }
            
            ssize_t sent = sendto(sock, packet.data(), total_size, 0,
                                 (struct sockaddr*)&server_addr, sizeof(server_addr));
            
            if (sent < 0) {
                perror("sendto");
            }
            
            // FPS monitoring
            fps_counter++;
            auto now = std::chrono::steady_clock::now();
            if (std::chrono::duration_cast<std::chrono::seconds>(now - last_fps_time).count() >= 1) {
                std::cout << "Streaming FPS: " << fps_counter 
                         << " | Frame size: " << total_size/1024 << "KB" << std::endl;
                fps_counter = 0;
                last_fps_time = now;
            }
        }
    }
    catch (const rs2::error& e) {
        std::cerr << "RealSense error: " << e.what() << std::endl;
    }
    
    close(sock);
    return 0;
}