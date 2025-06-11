#!/bin/bash
# Intel RealSense Setup Script for Raspberry Pi
# Run with: bash setup_raspberry_pi.sh

echo "🔧 Setting up Intel RealSense on Raspberry Pi..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
echo "📚 Installing system dependencies..."
sudo apt install -y \
    git cmake build-essential \
    libssl-dev libusb-1.0-0-dev \
    pkg-config libgtk-3-dev \
    libglfw3-dev libgl1-mesa-dev \
    libglu1-mesa-dev python3-dev \
    python3-pip

# Install librealsense2
echo "📷 Installing Intel RealSense SDK..."
sudo apt install -y librealsense2-dev librealsense2-utils

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install -r requirements.txt

# Try to install pyrealsense2
echo "🔗 Installing pyrealsense2 Python bindings..."
if pip install pyrealsense2; then
    echo "✅ pyrealsense2 installed successfully via pip"
else
    echo "⚠️  pip install failed, trying alternative method..."
    
    # Alternative: build from source
    echo "🛠️  Building pyrealsense2 from source (this may take a while)..."
    
    # Clone repository
    if [ ! -d "librealsense" ]; then
        git clone https://github.com/IntelRealSense/librealsense.git
    fi
    
    cd librealsense
    mkdir -p build && cd build
    
    # Configure build
    cmake .. \
        -DBUILD_PYTHON_BINDINGS=bool:true \
        -DPYTHON_EXECUTABLE=$(which python3) \
        -DCMAKE_BUILD_TYPE=Release
    
    # Build (using all available cores)
    make -j$(nproc)
    
    # Install
    sudo make install
    
    # Update library cache
    sudo ldconfig
    
    cd ../..
    echo "✅ Built and installed pyrealsense2 from source"
fi

# Set up USB permissions for RealSense
echo "🔐 Setting up USB permissions..."
sudo cp librealsense/config/99-realsense-libusb.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger

# Test installation
echo "🧪 Testing installation..."
python3 -c "import pyrealsense2 as rs; print('✅ pyrealsense2 imported successfully')" 2>/dev/null || {
    echo "❌ pyrealsense2 import failed"
    echo "💡 Try rebooting and running the test again"
    exit 1
}

echo ""
echo "🎉 Setup complete! You can now:"
echo "   1. Connect your RealSense camera"
echo "   2. Run: python3 test_camera.py"
echo "   3. If test passes, run: python3 main.py"
echo ""
echo "💡 If you encounter USB permission issues, try:"
echo "   sudo usermod -a -G plugdev $USER"
echo "   Then log out and back in, or reboot" 