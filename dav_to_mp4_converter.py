#!/usr/bin/env python3
"""
DAV to MP4 Batch Converter
Automatically converts DAV files to MP4 format with folder monitoring.
macOS optimized with QuickTime compatibility.
"""

import os
import sys
import subprocess
import json
import logging
from pathlib import Path
from datetime import datetime
import argparse
from typing import List, Tuple, Set
import hashlib
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('conversion.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FormatValidator:
    """Validate if a file is in a compatible format."""
    
    # macOS QuickTime compatible formats
    COMPATIBLE_FORMATS = {
        'mp4', 'mov', 'mkv', 'm4v', 'avi', 'wav', 'aiff', 'aac', 'mp3'
    }
    
    # Source formats that need conversion
    SOURCE_FORMATS = {'dav', 'dvr'}
    
    @staticmethod
    def get_file_extension(filepath: Path) -> str:
        """Get file extension without dot."""
        return filepath.suffix.lstrip('.').lower()
    
    @staticmethod
    def is_compatible(filepath: Path) -> bool:
        """Check if file is already in compatible format."""
        ext = FormatValidator.get_file_extension(filepath)
        return ext in FormatValidator.COMPATIBLE_FORMATS
    
    @staticmethod
    def needs_conversion(filepath: Path) -> bool:
        """Check if file needs conversion."""
        ext = FormatValidator.get_file_extension(filepath)
        return ext in FormatValidator.SOURCE_FORMATS
    
    @staticmethod
    def is_valid_media_file(filepath: Path) -> bool:
        """Check if file is a valid media file."""
        ext = FormatValidator.get_file_extension(filepath)
        return ext in (FormatValidator.COMPATIBLE_FORMATS | FormatValidator.SOURCE_FORMATS)


class MediaFileAnalyzer:
    """Analyze media files using FFprobe."""
    
    def __init__(self):
        self.ffprobe_available = self._check_ffprobe()
    
    @staticmethod
    def _check_ffprobe() -> bool:
        """Check if ffprobe is available."""
        try:
            subprocess.run(['ffprobe', '-version'], 
                         capture_output=True, timeout=5)
            return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def get_file_info(self, filepath: Path) -> dict:
        """Get detailed file information using ffprobe."""
        if not self.ffprobe_available:
            return self._get_basic_info(filepath)
        
        try:
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_format', '-show_streams',
                 '-print_json', str(filepath)],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
            logger.warning(f"ffprobe error for {filepath}: {e}")
        
        return self._get_basic_info(filepath)
    
    @staticmethod
    def _get_basic_info(filepath: Path) -> dict:
        """Get basic file information."""
        stat = filepath.stat()
        return {
            'filename': filepath.name,
            'size_bytes': stat.st_size,
            'modified_time': stat.st_mtime
        }
    
    def is_corrupted(self, filepath: Path) -> bool:
        """Check if file appears to be corrupted."""
        if filepath.stat().st_size == 0:
            return True
        
        if not self.ffprobe_available:
            return False
        
        try:
            result = subprocess.run(
                ['ffprobe', '-v', 'error', str(filepath)],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode != 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False


class MediaConverter:
    """Handle conversion of media files."""
    
    # macOS QuickTime optimized codecs
    CONVERSION_PRESETS = {
        'mp4_h264': {
            'codec_video': 'libx264',
            'codec_audio': 'aac',
            'crf': '23',
            'preset': 'medium',
            'ext': 'mp4'
        },
        'mp4_h265': {
            'codec_video': 'libx265',
            'codec_audio': 'aac',
            'crf': '23',
            'preset': 'medium',
            'ext': 'mp4'
        },
        'mov_prores': {
            'codec_video': 'prores',
            'codec_audio': 'aac',
            'prores_ks': '2',
            'ext': 'mov'
        },
        'mov_h264': {
            'codec_video': 'libx264',
            'codec_audio': 'aac',
            'crf': '23',
            'preset': 'medium',
            'ext': 'mov'
        }
    }
    
    def __init__(self, preset: str = 'mp4_h264', analyze_only: bool = False, replace_original: bool = False, backup_dir: Path = None):
        self.preset = preset
        self.analyze_only = analyze_only
        self.replace_original = replace_original
        self.backup_dir = backup_dir
        self.ffmpeg_available = self._check_ffmpeg()
        self.analyzer = MediaFileAnalyzer()
    
    @staticmethod
    def _check_ffmpeg() -> bool:
        """Check if ffmpeg is available."""
        try:
            subprocess.run(['ffmpeg', '-version'],
                         capture_output=True, timeout=5)
            return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def build_ffmpeg_command(self, input_file: Path, output_file: Path) -> List[str]:
        """Build ffmpeg command based on preset."""
        preset = self.CONVERSION_PRESETS.get(self.preset, self.CONVERSION_PRESETS['mp4_h264'])
        
        cmd = ['ffmpeg', '-i', str(input_file), '-y']
        
        # Video codec
        cmd.extend(['-c:v', preset['codec_video']])
        
        # Video quality settings
        if 'crf' in preset:
            cmd.extend(['-crf', preset['crf']])
        if 'preset' in preset:
            cmd.extend(['-preset', preset['preset']])
        if 'prores_ks' in preset:
            cmd.extend(['-prores_ks', preset['prores_ks']])
        
        # Audio codec
        cmd.extend(['-c:a', preset['codec_audio']])
        cmd.extend(['-b:a', '128k'])
        
        # macOS specific optimizations
        cmd.extend(['-movflags', '+faststart'])
        
        cmd.append(str(output_file))
        return cmd
    
    def convert(self, input_file: Path) -> Tuple[bool, str, Path]:
        """
        Convert a single file.
        Returns (success, message, output_path)
        """
        if not self.ffmpeg_available:
            return False, "ffmpeg not installed", input_file
        
        if self.analyzer.is_corrupted(input_file):
            return False, "File appears to be corrupted", input_file
        
        # Create temporary output file
        ext = self.CONVERSION_PRESETS[self.preset]['ext']
        temp_output = input_file.parent / f".{input_file.stem}_temp.{ext}"
        
        try:
            logger.info(f"Converting: {input_file.name} -> {ext.upper()}")
            
            cmd = self.build_ffmpeg_command(input_file, temp_output)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if result.returncode == 0 and temp_output.exists():
                original_size = input_file.stat().st_size
                converted_size = temp_output.stat().st_size
                ratio = (1 - converted_size / original_size) * 100
                
                # Backup original if requested
                if self.replace_original and self.backup_dir:
                    try:
                        self.backup_dir.mkdir(parents=True, exist_ok=True)
                        backup_path = self.backup_dir / input_file.name
                        shutil.copy2(input_file, backup_path)
                        logger.info(f"  Backed up original to: {backup_path}")
                    except Exception as e:
                        logger.warning(f"  Failed to backup: {e}")
                
                # Replace original or keep both
                if self.replace_original:
                    final_output = input_file
                    input_file.unlink()
                    temp_output.rename(final_output)
                    msg = f"✓ Replaced ({ratio:.1f}% size reduction)"
                else:
                    final_output = input_file.with_suffix(f'.{ext}')
                    temp_output.rename(final_output)
                    msg = f"✓ Converted ({ratio:.1f}% size reduction)"
                
                logger.info(f"  {msg}")
                return True, msg, final_output
            else:
                # Clean up temp file on failure
                if temp_output.exists():
                    temp_output.unlink()
                logger.error(f"Conversion failed: {result.stderr}")
                return False, f"Conversion failed: {result.stderr[:100]}", input_file
        
        except subprocess.TimeoutExpired:
            # Clean up temp file on timeout
            if temp_output.exists():
                temp_output.unlink()
            return False, "Conversion timeout (>1 hour)", input_file
        except Exception as e:
            # Clean up temp file on error
            if temp_output.exists():
                temp_output.unlink()
            return False, f"Error: {str(e)[:100]}", input_file


class FolderWatcher:
    """Monitor and manage folder-based conversions."""
    
    def __init__(self, folder: Path, converter: MediaConverter, skip_existing: bool = True):
        self.folder = Path(folder)
        self.converter = converter
        self.skip_existing = skip_existing
        self.converted_registry = self._load_registry()
        self.results = {'success': [], 'skipped': [], 'failed': []}
    
    def _get_registry_path(self) -> Path:
        """Get path to conversion registry file."""
        return self.folder / '.conversion_registry.json'
    
    def _load_registry(self) -> Set[str]:
        """Load previously converted files."""
        registry_path = self._get_registry_path()
        if not registry_path.exists():
            return set()
        
        try:
            with open(registry_path, 'r') as f:
                data = json.load(f)
                return set(data.get('converted_files', []))
        except (json.JSONDecodeError, IOError):
            return set()
    
    def _save_registry(self):
        """Save conversion registry."""
        registry_path = self._get_registry_path()
        try:
            with open(registry_path, 'w') as f:
                json.dump({
                    'converted_files': list(self.converted_registry),
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2)
        except IOError as e:
            logger.error(f"Failed to save registry: {e}")
    
    def _file_hash(self, filepath: Path) -> str:
        """Generate hash of file for comparison."""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read(8192)).hexdigest()
        except IOError:
            return ""
    
    def scan_folder(self) -> Tuple[List[Path], List[Path], List[Path]]:
        """
        Scan folder and categorize files.
        Returns (files_to_convert, already_compatible, all_files)
        """
        if not self.folder.exists():
            logger.error(f"Folder not found: {self.folder}")
            return [], [], []
        
        to_convert = []
        compatible = []
        all_files = []
        
        logger.info(f"Scanning folder: {self.folder}")
        
        for filepath in self.folder.rglob('*'):
            if not filepath.is_file():
                continue
            
            if not FormatValidator.is_valid_media_file(filepath):
                continue
            
            all_files.append(filepath)
            
            # Check if already converted
            file_id = f"{filepath.name}:{self._file_hash(filepath)}"
            if file_id in self.converted_registry:
                compatible.append(filepath)
                continue
            
            # Check format
            if FormatValidator.is_compatible(filepath):
                compatible.append(filepath)
            elif FormatValidator.needs_conversion(filepath):
                to_convert.append(filepath)
        
        logger.info(f"Found {len(all_files)} media files")
        logger.info(f"  {len(compatible)} already compatible")
        logger.info(f"  {len(to_convert)} need conversion")
        
        return to_convert, compatible, all_files
    
    def process_folder(self, dry_run: bool = False) -> dict:
        """
        Process all files in folder.
        Returns results summary.
        """
        to_convert, compatible, _ = self.scan_folder()
        
        logger.info(f"\n{'=' * 60}")
        logger.info(f"Starting batch conversion | DRY RUN: {dry_run}")
        if self.converter.replace_original:
            logger.info(f"MODE: Replace original files")
            if self.converter.backup_dir:
                logger.info(f"BACKUPS: {self.converter.backup_dir}")
        else:
            logger.info(f"MODE: Keep original + create converted copy")
        logger.info(f"{'=' * 60}\n")
        
        for i, filepath in enumerate(to_convert, 1):
            logger.info(f"\n[{i}/{len(to_convert)}] Processing: {filepath.name}")
            
            if dry_run:
                mode = "Replace" if self.converter.replace_original else "Create copy"
                self.results['skipped'].append({
                    'file': filepath.name,
                    'reason': f'DRY RUN ({mode})'
                })
                continue
            
            success, message, output_path = self.converter.convert(filepath)
            
            if success:
                self.converted_registry.add(f"{filepath.name}:{self._file_hash(filepath)}")
                self.results['success'].append({
                    'file': filepath.name,
                    'message': message,
                    'output': output_path.name
                })
            else:
                self.results['failed'].append({
                    'file': filepath.name,
                    'reason': message
                })
        
        self._save_registry()
        self._print_summary()
        return self.results
    
    def _print_summary(self):
        """Print conversion summary."""
        print(f"\n{'=' * 60}")
        print("CONVERSION SUMMARY")
        print(f"{'=' * 60}")
        print(f"✓ Successful:  {len(self.results['success'])}")
        print(f"⊘ Skipped:     {len(self.results['skipped'])}")
        print(f"✗ Failed:      {len(self.results['failed'])}")
        print(f"{'=' * 60}\n")
        
        if self.results['failed']:
            print("FAILED CONVERSIONS:")
            for item in self.results['failed']:
                print(f"  • {item['file']}: {item['reason']}")
            print()


def main():
    parser = argparse.ArgumentParser(
        description='Batch convert DAV files to MP4 for macOS QuickTime',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s /path/to/folder
  %(prog)s /path/to/folder --replace-original
  %(prog)s /path/to/folder --replace-original --backup-dir /path/to/backups
  %(prog)s /path/to/folder --preset mov_h264
  %(prog)s /path/to/folder --dry-run
        '''
    )
    
    parser.add_argument(
        'folder',
        help='Folder containing DAV files'
    )
    
    parser.add_argument(
        '--preset',
        choices=list(MediaConverter.CONVERSION_PRESETS.keys()),
        default='mp4_h264',
        help='Conversion preset (default: mp4_h264)'
    )
    
    parser.add_argument(
        '--replace-original',
        action='store_true',
        help='Replace original DAV files with converted versions'
    )
    
    parser.add_argument(
        '--backup-dir',
        type=str,
        help='Directory to backup original files before replacing (requires --replace-original)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be converted without actually converting'
    )
    
    parser.add_argument(
        '--analyze-only',
        action='store_true',
        help='Only analyze files without converting'
    )
    
    parser.add_argument(
        '--no-skip-existing',
        action='store_true',
        help='Do not skip already converted files'
    )
    
    args = parser.parse_args()
    
    # Validate backup directory option
    if args.backup_dir and not args.replace_original:
        logger.error("--backup-dir requires --replace-original flag")
        sys.exit(1)
    
    # Check dependencies
    converter = MediaConverter(
        preset=args.preset,
        analyze_only=args.analyze_only,
        replace_original=args.replace_original,
        backup_dir=Path(args.backup_dir) if args.backup_dir else None
    )
    
    if not converter.ffmpeg_available:
        logger.error("❌ ffmpeg is not installed")
        logger.error("Install ffmpeg:")
        logger.error("  macOS: brew install ffmpeg")
        sys.exit(1)
    
    logger.info(f"FFmpeg available: ✓")
    logger.info(f"FFprobe available: {'✓' if converter.analyzer.ffprobe_available else '⊘'}")
    logger.info(f"Conversion preset: {args.preset}")
    
    # Run conversion
    watcher = FolderWatcher(args.folder, converter, skip_existing=not args.no_skip_existing)
    results = watcher.process_folder(dry_run=args.dry_run or args.analyze_only)
    
    # Exit with error if any conversions failed
    sys.exit(0 if not results['failed'] else 1)


if __name__ == '__main__':
    main()
