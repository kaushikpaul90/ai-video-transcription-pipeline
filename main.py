#!/usr/bin/env python3
"""Root-level entry point for VideoTranscriber.

This module imports and runs the actual main module from the reorganized structure.
"""
import sys
from pathlib import Path

# Add src directory to path so we can import video_transcriber
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run the main module
from src.video_transcriber import main

if __name__ == "__main__":
    main.main()
