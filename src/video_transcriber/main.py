"""CLI entrypoint for VideoTranscriber.

Usage:
    python main.py path/to/video.mp4
    python main.py path/to/video.mp4 --output out --no-keep-raw
"""
from __future__ import annotations

import argparse
import sys

from . import pipeline


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="VideoTranscriber",
        description="Ingest a video, transcribe it, and produce well-structured content "
        "using Azure AI Foundry.",
    )
    parser.add_argument("video", help="Path to the input video file (mp4, mov, mkv, ...).")
    parser.add_argument(
        "-o", "--output", default="output", help="Output directory (default: ./output)."
    )
    parser.add_argument(
        "--no-keep-raw",
        action="store_true",
        help="Do not write the raw transcript .txt file.",
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    try:
        result = pipeline.run(
            video_path=args.video,
            output_dir=args.output,
            keep_raw=not args.no_keep_raw,
        )
    except Exception as exc:  # surface a clean message to the user
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print("\nDone.")
    if not args.no_keep_raw:
        print(f"  Raw transcript : {result.raw_transcript_path}")
    print(f"  Structured doc : {result.structured_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
