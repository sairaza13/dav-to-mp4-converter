#!/bin/bash
# Batch DAV to MP4 Converter - Easy wrapper script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/dav_to_mp4_converter.py"

# Check if Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "❌ Error: dav_to_mp4_converter.py not found in $SCRIPT_DIR"
    exit 1
fi

# Check dependencies
check_dependency() {
    if ! command -v "$1" &> /dev/null; then
        echo "❌ $1 is not installed"
        echo "Install via: brew install $1"
        exit 1
    fi
}

check_dependency "python3"
check_dependency "ffmpeg"

# Run the converter
python3 "$PYTHON_SCRIPT" "$@"
