#!/bin/bash
# One-command installer for DAV to MP4 Converter

set -e

echo "🎬 DAV to MP4 Converter Installer"
echo "================================="
echo ""

# Check if already installed
if [ -d "$HOME/dav-converter" ] && [ -f "$HOME/dav-converter/dav_to_mp4_converter.py" ]; then
    echo "✓ Already installed at ~/dav-converter"
    echo "Update: curl -fsSL https://raw.githubusercontent.com/sairaza13/dav-to-mp4-converter/main/install.sh | bash"
    exit 0
fi

# Check dependencies
echo "Checking dependencies..."
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not installed"
    echo "Install from: https://brew.sh"
    exit 1
fi

echo "Installing ffmpeg..."
brew install ffmpeg > /dev/null 2>&1 || echo "⊘ ffmpeg already installed"

# Create directory
echo "Creating ~/dav-converter directory..."
mkdir -p ~/dav-converter
cd ~/dav-converter

# Download script
echo "Downloading converter script..."
curl -fsSL https://raw.githubusercontent.com/sairaza13/dav-to-mp4-converter/main/dav_to_mp4_converter.py -o dav_to_mp4_converter.py
curl -fsSL https://raw.githubusercontent.com/sairaza13/dav-to-mp4-converter/main/batch_convert.sh -o batch_convert.sh

# Make executable
chmod +x dav_to_mp4_converter.py batch_convert.sh

# Create alias
echo "Creating alias..."
echo "alias dav-convert='python3 ~/dav-converter/dav_to_mp4_converter.py'" >> ~/.zshrc
echo "alias dav-convert='python3 ~/dav-converter/dav_to_mp4_converter.py'" >> ~/.bash_profile

echo ""
echo "✅ Installation complete!"
echo ""
echo "Usage:"
echo "  dav-convert /path/to/videos"
echo "  dav-convert /path/to/videos --replace-original"
echo "  dav-convert /path/to/videos --replace-original --backup-dir ~/dav-backups"
echo ""
echo "Or with full path:"
echo "  python3 ~/dav-converter/dav_to_mp4_converter.py /path/to/videos"
echo ""
echo "For more help:"
echo "  python3 ~/dav-converter/dav_to_mp4_converter.py --help"
