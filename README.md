# DAV to MP4 Batch Converter

Automatically convert DAV surveillance files to MP4 format optimized for macOS QuickTime viewing. Features intelligent folder monitoring, format detection, and conversion tracking.

## Features

✓ **Batch processing** - Convert entire folders recursively  
✓ **Smart detection** - Automatically skips already-compatible formats  
✓ **Corruption detection** - Identifies and skips damaged files  
✓ **Conversion tracking** - Registry prevents re-converting files  
✓ **Multiple presets** - H.264, H.265, ProRes formats  
✓ **macOS optimized** - QuickTime native container optimization  
✓ **Detailed logging** - Full conversion history with timestamps  
✓ **Dry-run mode** - Preview conversions before executing  

## Installation

### Prerequisites

```bash
# Install ffmpeg (includes ffprobe)
brew install ffmpeg

# Python 3.7+ (usually pre-installed on macOS)
python3 --version
```

### Setup

1. Clone or download this project
2. Make scripts executable:
   ```bash
   chmod +x batch_convert.sh dav_to_mp4_converter.py
   ```

3. Optional: Add to PATH for global access
   ```bash
   sudo ln -s /path/to/batch_convert.sh /usr/local/bin/dav-convert
   ```

## Usage

### Basic Usage

```bash
# Convert all DAV files in a folder
./batch_convert.sh /path/to/videos

# Or directly with Python
python3 dav_to_mp4_converter.py /path/to/videos
```

### Preview Conversions (Dry-Run)

```bash
./batch_convert.sh /path/to/videos --dry-run
```

### Choose Conversion Format

```bash
# Standard H.264 (best compatibility)
./batch_convert.sh /path/to/videos --preset mp4_h264

# Modern H.265 (smaller file size)
./batch_convert.sh /path/to/videos --preset mp4_h265

# Professional ProRes MOV
./batch_convert.sh /path/to/videos --preset mov_prores

# QuickTime native MOV
./batch_convert.sh /path/to/videos --preset mov_h264
```

### Analyze Files Only

```bash
./batch_convert.sh /path/to/videos --analyze-only
```

### Force Re-conversion

```bash
# By default, converted files are tracked and skipped
# To reconvert everything:
./batch_convert.sh /path/to/videos --no-skip-existing
```

## Output Formats Explained

### MP4 H.264 (Default)
- **Best for**: Compatibility, streaming, general use
- **File size**: Medium
- **Quality**: Excellent
- **QuickTime**: Native support
- **Use case**: General purpose surveillance archives

### MP4 H.265
- **Best for**: Modern systems, smaller files
- **File size**: ~40% smaller than H.264
- **Quality**: Excellent
- **QuickTime**: Requires 10.13+
- **Use case**: Long-term storage, bandwidth-constrained

### ProRes MOV
- **Best for**: Professional editing, archival
- **File size**: Larger
- **Quality**: Professional (visually lossless)
- **QuickTime**: Excellent support
- **Use case**: Professional post-production, high-value archives

### MOV H.264
- **Best for**: Maximum QuickTime integration
- **File size**: Medium
- **Quality**: Excellent
- **QuickTime**: Native (preferred container)
- **Use case**: Direct QuickTime editing compatibility

## File Organization

```
your_video_folder/
├── camera1/
│   ├── 2024-01-15.dav         → converted to MP4
│   ├── 2024-01-15.mp4         (skipped - already compatible)
│   └── 2024-01-16.dav         → converted to MP4
├── camera2/
│   └── backup.dav             → converted to MP4
├── .conversion_registry.json   (auto-generated tracking file)
└── conversion.log             (auto-generated log file)
```

## Conversion Registry

The tool automatically creates `.conversion_registry.json` to track which files have been converted. This prevents re-converting the same file multiple times.

To reset tracking:
```bash
rm /path/to/videos/.conversion_registry.json
```

## Logging

All conversions are logged to `conversion.log` in the working directory:

```
2024-01-15 10:23:45 - INFO - Scanning folder: /path/to/videos
2024-01-15 10:23:45 - INFO - Found 5 media files
2024-01-15 10:23:45 - INFO - [1/3] Processing: camera_001.dav
2024-01-15 10:24:12 - INFO - ✓ camera_001.dav: Success (45.3% size reduction)
```

## Troubleshooting

### "ffmpeg not installed"
```bash
brew install ffmpeg
```

### Conversion is slow
- This is normal for DAV files (typically low-quality)
- Reduce quality with different preset settings
- Larger files naturally take longer

### File appears corrupted
The tool skips files with:
- Zero byte size
- Invalid header/metadata
- Timeout during conversion (>1 hour)

### QuickTime won't play the file
Try different presets:
```bash
# Use MOV native format
./batch_convert.sh /path/to/videos --preset mov_h264
```

### Conversion stopped mid-way
Check `conversion.log` for error details:
```bash
tail -50 conversion.log
```

## Performance Tips

1. **Process in batches** if you have thousands of files
2. **Use H.265** preset for storage optimization (40% smaller)
3. **Close other apps** to free system resources
4. **Use SSD storage** for faster conversion
5. **Monitor temp space** - conversions create temp files

## System Requirements

- macOS 10.12+
- Python 3.7+
- ffmpeg (via Homebrew: `brew install ffmpeg`)
- Minimum 5GB free disk space (for conversion temp files)

## License

MIT License - Free to use and modify

## Support

For issues or feature requests, check the logs:
```bash
tail -f conversion.log
```

Common solutions:
- Update ffmpeg: `brew upgrade ffmpeg`
- Reset tracking: `rm .conversion_registry.json`
- Verify ffmpeg: `ffmpeg -version`