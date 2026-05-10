# Quick Start Guide

## 1-Minute Setup

```bash
# Download and install
curl -fsSL https://raw.githubusercontent.com/sairaza13/dav-to-mp4-converter/main/install.sh | bash

# Reload shell
source ~/.zshrc
```

## Convert Your Files

```bash
# Replace originals with MP4
dav-convert /path/to/videos --replace-original

# OR with backup
dav-convert /path/to/videos --replace-original --backup-dir ~/dav-backups

# OR keep both (create new MP4 files)
dav-convert /path/to/videos
```

## Find Your Videos

```bash
# Search for DAV files
find ~ -name "*.dav" -type f 2>/dev/null | head -5

# Or check common locations
ls ~/Videos/
ls /Volumes/
```

## Preset Quick Reference

| Preset | File Size | Quality | Speed | Use Case |
|--------|-----------|---------|-------|----------|
| `mp4_h264` | Medium | Excellent | Fast | ⭐ Default, best compatibility |
| `mp4_h265` | Small | Excellent | Slower | 40% smaller, modern systems |
| `mov_prores` | Large | Professional | Slower | Editing, archival |
| `mov_h264` | Medium | Excellent | Fast | Maximum QuickTime native |

## Example Commands

```bash
# Dry-run to preview
dav-convert /path --dry-run

# Small file size (40% reduction)
dav-convert /path --preset mp4_h265

# Maximum QuickTime compatibility
dav-convert /path --preset mov_h264

# Professional archival
dav-convert /path --preset mov_prores

# Replace originals with backup
dav-convert /path --replace-original --backup-dir ~/dav-backups
```

## Troubleshooting

```bash
# Check if ffmpeg is installed
ffmpeg -version

# Update ffmpeg
brew upgrade ffmpeg

# View conversion logs
tail -50 conversion.log

# Reset tracking (reconvert everything)
rm /path/to/videos/.conversion_registry.json
```

That's it! 🎉
