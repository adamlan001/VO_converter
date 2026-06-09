#!/usr/bin/env python3
"""Minimal CLI entrypoint for VO_converter."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert audio/video files with ffmpeg.")
    parser.add_argument("input_file", type=Path, help="Path to the input media file")
    parser.add_argument("output_file", type=Path, help="Path to the output media file")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite output file if it already exists",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not args.input_file.exists():
        print(f"Input file does not exist: {args.input_file}", file=sys.stderr)
        return 1

    if args.output_file.exists() and not args.overwrite:
        print(
            f"Output file already exists: {args.output_file}. Use --overwrite to replace it.",
            file=sys.stderr,
        )
        return 1

    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        print("ffmpeg is not installed or not available in PATH.", file=sys.stderr)
        return 1

    command = [ffmpeg, "-i", str(args.input_file)]
    if args.overwrite:
        command.append("-y")
    else:
        command.append("-n")
    command.append(str(args.output_file))

    result = subprocess.run(command, check=False)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
