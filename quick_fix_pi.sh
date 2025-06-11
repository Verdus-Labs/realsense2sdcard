#!/bin/bash
# Quick fix for pyrealsense2 installation issues on Raspberry Pi

echo "🔧 Quick Fix for pyrealsense2 on Raspberry Pi"
echo "=============================================="

# First, let's diagnose the issue
echo "📊 Running diagnostics..."
python3 diagnose_realsense.py

echo ""
echo "🛠️  Attempting to fix pyrealsense2 installation..."

# Remove any existing broken installation
echo "🗑️  Removing existing pyrealsense2..."
pip uninstall -y pyrealsense2 2>/dev/null || true

# Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt update
sudo apt install -y librealsense2-dev librealsense2-utils

# Try pip install first
echo "🐍 Attempting pip install..."
if pip install pyrealsense2; then
    echo "✅ Successfully installed pyrealsense2 via pip"
    
    # Test the installation
    echo "🧪 Testing installation..."
    if python3 -c "import pyrealsense2 as rs; ctx = rs.context(); print('✅ pyrealsense2 working correctly')"; then
        echo "🎉 Installation successful!"
        exit 0
    else
        echo "❌ Installation test failed"
    fi
else
    echo "⚠️  pip install failed, trying alternative approach..."
fi

# Alternative: Check if system installation exists
echo "🔍 Checking for system installation..."
if python3 -c "import sys; sys.path.insert(0, '/usr/lib/python3/dist-packages'); import pyrealsense2 as rs; print('Found system installation')" 2>/dev/null; then
    echo "💡 Found system installation, creating symlink..."
    
    # Find the Python site-packages directory
    SITE_PACKAGES=$(python3 -c "import site; print(site.getsitepackages()[0])")
    
    # Create symlink to system installation
    sudo ln -sf /usr/lib/python3/dist-packages/pyrealsense2* "$SITE_PACKAGES/"
    
    echo "🔗 Created symlink to system installation"
else
    echo "📥 No system installation found, installing from apt..."
    sudo apt install -y python3-pyrealsense2 || {
        echo "❌ apt installation also failed"
        echo "🛠️  You may need to build from source using: bash setup_raspberry_pi.sh"
        exit 1
    }
fi

# Final test
echo "🧪 Final test..."
if python3 -c "import pyrealsense2 as rs; ctx = rs.context(); print('✅ pyrealsense2 working correctly')"; then
    echo ""
    echo "🎉 SUCCESS! pyrealsense2 is now working"
    echo "💡 You can now run: python3 test_camera.py"
else
    echo ""
    echo "❌ Installation still not working"
    echo "🔧 Try running the full setup: bash setup_raspberry_pi.sh"
    exit 1
fi 