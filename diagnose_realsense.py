#!/usr/bin/env python3
"""
Diagnostic script to check pyrealsense2 installation and availability.
"""

import sys
import os

def check_pyrealsense2():
    """Check pyrealsense2 installation and available attributes."""
    print("🔍 Diagnosing pyrealsense2 installation...")
    print("=" * 50)
    
    # Check if pyrealsense2 can be imported
    try:
        import pyrealsense2
        print("✅ pyrealsense2 module imported successfully")
        print(f"📍 Module location: {pyrealsense2.__file__}")
        print(f"🏷️  Module version: {getattr(pyrealsense2, '__version__', 'Unknown')}")
    except ImportError as e:
        print(f"❌ Failed to import pyrealsense2: {e}")
        return False
    
    # Check available attributes
    print("\n🔧 Available attributes in pyrealsense2:")
    attrs = dir(pyrealsense2)
    for attr in sorted(attrs):
        if not attr.startswith('_'):
            print(f"   - {attr}")
    
    # Check for essential classes
    essential_attrs = ['context', 'pipeline', 'config', 'stream', 'format']
    missing_attrs = []
    
    print("\n🎯 Checking essential attributes:")
    for attr in essential_attrs:
        if hasattr(pyrealsense2, attr):
            print(f"   ✅ {attr}")
        else:
            print(f"   ❌ {attr} - MISSING")
            missing_attrs.append(attr)
    
    if missing_attrs:
        print(f"\n⚠️  Missing essential attributes: {missing_attrs}")
        print("This suggests an incomplete installation.")
        return False
    
    # Try to create a context
    print("\n📷 Testing context creation:")
    try:
        import pyrealsense2 as rs
        ctx = rs.context()
        print("   ✅ Context created successfully")
        
        # Check for devices
        devices = ctx.query_devices()
        print(f"   📱 Found {len(devices)} device(s)")
        
        return True
    except Exception as e:
        print(f"   ❌ Failed to create context: {e}")
        return False

def check_system_libs():
    """Check if system librealsense2 is installed."""
    print("\n🔧 Checking system libraries:")
    
    # Check for pkg-config
    pkg_config_result = os.system("pkg-config --exists realsense2 2>/dev/null")
    if pkg_config_result == 0:
        print("   ✅ librealsense2 found via pkg-config")
        os.system("pkg-config --modversion realsense2")
    else:
        print("   ❌ librealsense2 not found via pkg-config")
    
    # Check for library files
    lib_paths = [
        "/usr/lib/librealsense2.so",
        "/usr/local/lib/librealsense2.so",
        "/usr/lib/x86_64-linux-gnu/librealsense2.so",
        "/usr/lib/aarch64-linux-gnu/librealsense2.so",
        "/usr/lib/arm-linux-gnueabihf/librealsense2.so"
    ]
    
    found_lib = False
    for lib_path in lib_paths:
        if os.path.exists(lib_path):
            print(f"   ✅ Found library: {lib_path}")
            found_lib = True
            break
    
    if not found_lib:
        print("   ❌ No librealsense2 library found")

def suggest_fixes():
    """Suggest potential fixes based on the diagnosis."""
    print("\n💡 Suggested fixes:")
    print("=" * 30)
    
    print("1. 🔄 Reinstall pyrealsense2:")
    print("   pip uninstall pyrealsense2")
    print("   pip install pyrealsense2")
    
    print("\n2. 📦 Install system libraries (if missing):")
    print("   sudo apt update")
    print("   sudo apt install -y librealsense2-dev librealsense2-utils")
    
    print("\n3. 🛠️  Build from source (if pip fails):")
    print("   bash setup_raspberry_pi.sh")
    
    print("\n4. 🔍 Check virtual environment:")
    print("   which python3")
    print("   pip list | grep realsense")
    
    print("\n5. ♻️  Try system Python (outside venv):")
    print("   deactivate")
    print("   python3 -c 'import pyrealsense2 as rs; print(rs.__version__)'")

def main():
    """Main diagnostic function."""
    print("Intel RealSense Diagnostic Tool")
    print("=" * 40)
    
    print(f"🐍 Python version: {sys.version}")
    print(f"📁 Current working directory: {os.getcwd()}")
    print(f"🎯 Python executable: {sys.executable}")
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("🔧 Running in virtual environment")
    else:
        print("🌍 Running in system Python")
    
    print()
    
    # Run diagnostics
    realsense_ok = check_pyrealsense2()
    check_system_libs()
    
    if not realsense_ok:
        suggest_fixes()
    else:
        print("\n🎉 All checks passed! pyrealsense2 should work correctly.")

if __name__ == "__main__":
    main() 