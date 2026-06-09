#!/usr/bin/env python3
"""Minimal CLI entrypoint for VO_converter."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

FFMPEG_TIMEOUT_SECONDS = 3600


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("timeout must be a positive integer")
    return parsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert audio/video files with ffmpeg.")
    parser.add_argument("input_file", type=Path, help="Path to the input media file")
    parser.add_argument("output_file", type=Path, help="Path to the output media file")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite output file if it already exists",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=positive_int,
        default=FFMPEG_TIMEOUT_SECONDS,
        help=f"Maximum ffmpeg runtime in seconds (default: {FFMPEG_TIMEOUT_SECONDS})",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not args.input_file.exists():
        print(f"Input file does not exist: {args.input_file}", file=sys.stderr)
        return 1

    if not args.input_file.is_file():
        print(f"Input path is not a file: {args.input_file}", file=sys.stderr)
        return 1

    if args.output_file.exists() and args.output_file.is_dir():
        print(f"Output path is a directory: {args.output_file}", file=sys.stderr)
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
    command.append(str(args.output_file))

    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=args.timeout_seconds,
        )
    except subprocess.TimeoutExpired:
        print(f"ffmpeg timed out after {args.timeout_seconds} seconds.", file=sys.stderr)
        return 1

    if result.returncode != 0 and result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
