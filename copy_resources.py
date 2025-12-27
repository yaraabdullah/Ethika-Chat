#!/usr/bin/env python3
"""
Helper script to copy markdown resource files to the resources directory.
"""
import argparse
import shutil
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Copy markdown resource files to resources directory"
    )
    parser.add_argument(
        '--source',
        type=str,
        default='/Users/yara/Downloads',
        help='Source directory containing .md files'
    )
    parser.add_argument(
        '--dest',
        type=str,
        default='./resources',
        help='Destination directory (default: ./resources)'
    )
    parser.add_argument(
        '--pattern',
        type=str,
        default='RES-*.md',
        help='File pattern to match (default: RES-*.md)'
    )
    
    args = parser.parse_args()
    
    source_dir = Path(args.source)
    dest_dir = Path(args.dest)
    
    if not source_dir.exists():
        print(f"Error: Source directory not found: {source_dir}")
        return
    
    # Create destination directory
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all matching files
    md_files = list(source_dir.glob(args.pattern))
    
    if not md_files:
        print(f"No files matching pattern '{args.pattern}' found in {source_dir}")
        return
    
    print(f"Found {len(md_files)} files matching '{args.pattern}'")
    print(f"Copying to: {dest_dir}\n")
    
    copied = 0
    for md_file in md_files:
        dest_file = dest_dir / md_file.name
        if dest_file.exists():
            print(f"  ⚠ Skipping {md_file.name} (already exists)")
        else:
            shutil.copy2(md_file, dest_file)
            print(f"  ✓ Copied {md_file.name}")
            copied += 1
    
    print(f"\n✓ Copied {copied} new files to {dest_dir}")
    print(f"  Total files in destination: {len(list(dest_dir.glob('*.md')))}")


if __name__ == "__main__":
    main()

