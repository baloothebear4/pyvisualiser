#!/bin/bash
#
# KMS/DRM Pygame Setup Script for Raspberry Pi 5 (Lite OS)
#
# This script automates the installation of system dependencies,
# custom compilation of SDL2 with kmsdrm support, and source compilation
# of Pygame to ensure it correctly initializes on DSI screens without X/Wayland.
#
# IMPORTANT: This script assumes it is executed from the root directory
# of the 'pyvisualiser' project repository.
#
# Author: Gemini
# Date: October 2025
#
set -e # Exit immediately if a command exits with a non-zero status.

# --- Configuration ---
SDL_VERSION="2.28.5"
SDL_ARCHIVE="SDL2-${SDL_VERSION}.tar.gz"
VENV_DIR="venv"

echo "Starting Pygame KMS/DRM Automated Setup for RPi 5..."
echo "--------------------------------------------------------"

# 1. Install System Build Tools and Development Libraries
echo "1. Installing system build tools, Python dependencies, and development libraries (including image support)..."
sudo apt update
# Relying on system default Python (likely 3.12+) and its associated packages
sudo apt install -y build-essential git \
    python3-dev python3-venv \
    libudev-dev libgbm-dev libdrm-dev \
    libfreetype-dev libsdl2-ttf-dev \
    libsdl2-image-dev \
    libjpeg-dev libpng-dev \
    libgbm1 \
    wget

# 2. Custom Compile and Install SDL2 with KMS/DRM Support
# The standard repository SDL2 often lacks the kmsdrm backend.

if [ -f /usr/local/lib/libSDL2-2.0.so.0 ]; then
    echo "2. Custom SDL2 library already found in /usr/local/lib. Skipping re-compilation."
else
    echo "2. Compiling SDL2 (v${SDL_VERSION}) with KMS/DRM enabled..."

    # Remove potentially conflicting system-installed SDL2 runtime
    sudo apt remove -y libsdl2-2.0-0

    # Temporarily move to /tmp for compilation
    CURRENT_DIR=$(pwd)
    cd /tmp

    # Download and extract SDL2 source
    wget -nc "https://github.com/libsdl-org/SDL/releases/download/release-${SDL_VERSION}/${SDL_ARCHIVE}"
    tar -xzvf "${SDL_ARCHIVE}"
    cd "SDL2-${SDL_VERSION}"

    # Configure: Explicitly enable KMS/DRM
    ./configure --disable-video-x11 --disable-video-wayland --enable-video-kmsdrm

    # Compile and install
    make -j$(nproc)
    sudo make install

    # Update the linker cache so Pygame can find the new library
    sudo ldconfig

    echo "   SDL2 installed successfully to /usr/local/lib."

    # Return to the original project directory
    cd "${CURRENT_DIR}"
fi

# 3. Configure System Files (config.txt and asound.conf)
echo "3. Configuring system files..."

# Copy config.txt to /boot/firmware/ (using sudo)
if [ -f "scripts/config.txt" ]; then
    echo "   Copying scripts/config.txt to /boot/firmware/"
    sudo cp "scripts/config.txt" /boot/firmware/
else
    echo "   WARNING: scripts/config.txt not found. Skipping config.txt copy."
fi

# Copy asound.conf to /etc/ (using sudo)
if [ -f "scripts/asound.conf" ]; then
    echo "   Copying scripts/asound.conf to /etc/"
    sudo cp "scripts/asound.conf" /etc/
else
    echo "   WARNING: scripts/asound.conf not found. Skipping asound.conf copy."
fi

# 4. Setup Virtual Environment (Project assumed to be current directory)
echo "4. Setting up virtual environment using the system default Python..."

VENV_CREATE_CMD="python3 -m venv ${VENV_DIR}"
PYTHON_USED="system default (likely 3.12+)"

if [ ! -d "${VENV_DIR}" ]; then
    echo "   Attempting to create venv using: ${PYTHON_USED}"
    ${VENV_CREATE_CMD}
else
    echo "   Virtual environment already exists. Using existing venv with Python ${PYTHON_USED}."
fi

source "${VENV_DIR}/bin/activate"

# 5. Force Pygame Source Compilation (Critical Step)
echo "5. Installing Pygame from source to ensure KMS/DRM, Font, and Image support..."

# --- HARDENING Pygame Compilation ---
# CRITICAL: Explicitly set PATH, CFLAGS, and LDFLAGS to include /usr/local/ directories
# This forces Pygame's setup to find the custom compiled SDL2 headers, libraries, and sdl-config tool.
export PATH="/usr/local/bin:$PATH"
export CFLAGS="-I/usr/local/include/SDL2 $CFLAGS"
export LDFLAGS="-L/usr/local/lib $LDFLAGS"
# --- END HARDENING ---

# Purge pip cache to prevent using previously downloaded incompatible wheels
pip cache purge

# Uninstall any existing Pygame
pip uninstall -y pygame

# Install Pygame forcing source compilation and ignoring cache
# --no-binary :all: is crucial for forcing the link to the custom SDL libraries
pip install --no-binary :all: --no-cache-dir pygame

# Clear environment variables after successful Pygame installation
unset CFLAGS
unset LDFLAGS
unset PATH # Unset PATH modification

# 6. Install Remaining Dependencies
echo "6. Installing remaining Python dependencies from requirements.txt..."
if [ -f "requirements.txt" ]; then
    # We must uninstall pygame again here if it was a dependency in requirements.txt to avoid double installation errors,
    # but since it was installed in step 5, we can just proceed.
    pip install -r requirements.txt
else
    echo "   WARNING: requirements.txt not found. Only Pygame has been installed."
fi

echo "--------------------------------------------------------"
echo "✅ Setup Complete!"
echo "A reboot is recommended for the new config.txt and asound.conf to take effect."
echo "To run your application, you MUST explicitly set the library path and video driver. Use the following commands:"
echo "   source venv/bin/activate"
echo "   export LD_LIBRARY_PATH=/usr/local/lib:\$LD_LIBRARY_PATH"
echo "   export SDL_VIDEODRIVER=kmsdrm"
echo "   python your_main_application.py"
