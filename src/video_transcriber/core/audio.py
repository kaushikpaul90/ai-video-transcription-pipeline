"""Audio extraction and chunking for long  cross-platform (Windows/macOS/Linux).videos 

A single streaming ffmpeg pass converts the video to low-bitrate, mono, 16 kHz MP3 and
splits it into fixed-duration segments at the same time. This:
  * never loads the whole audio track into memory (handles multi-hour videos);
  * produces small uploads (low-bitrate MP3) that stay well under the ~25 MB STT limit
    and keep transcription fast/cheap;
  * relies only on ffmpeg (no pydub), so it behaves identically on every platform.
"""
from __future__ import annotations

import glob
import os
import shutil
import subprocess
import tempfile
from typing import List


def _require_ffmpeg() -> None:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "ffmpeg was not found on PATH. Install it (https://ffmpeg.org/download.html) "
            "and ensure 'ffmpeg' is runnable from a terminal.\n"
            "  Windows: winget install Gyan.FFmpeg   |   macOS: brew install ffmpeg"
        )


def extract_and_segment(
    video_path: str,
    workdir: str,
    chunk_seconds: int,
    bitrate: str = "32k",
) -> List[str]:
    """Extract audio and split it into <= chunk_seconds MP3 segments in one ffmpeg pass.

    Returns an ordered list of chunk file paths. Short videos yield a single chunk.
    Uses optimized libmp3lame settings for faster encoding.
    """
    _require_ffmpeg()
    
    # Resolve video path: check current location, then data/ subdirectory
    resolved_path = video_path
    if not os.path.isfile(resolved_path):
        data_path = os.path.join(os.getcwd(), "data", video_path)
        if os.path.isfile(data_path):
            resolved_path = data_path
        else:
            raise FileNotFoundError(
                f"Video file not found: {video_path}\n"
                f"  Checked: {video_path} and data/{video_path}"
            )
    
    video_path = resolved_path

    chunk_dir = os.path.join(workdir, "chunks")
    os.makedirs(chunk_dir, exist_ok=True)
    pattern = os.path.join(chunk_dir, "chunk_%04d.mp3")

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vn",                       # drop video
        "-ac", "1",                  # mono
        "-ar", "16000",              # 16 kHz (plenty for speech STT)
        "-c:a", "libmp3lame",
        "-b:a", bitrate,             # low bitrate -> tiny, cheap uploads
        "-q:a", "9",                 # quality 9 = fast encoding with acceptable quality
        "-f", "segment",
        "-segment_time", str(max(1, chunk_seconds)),
        "-reset_timestamps", "1",
        pattern,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed to process audio:\n{result.stderr[-2000:]}")

    chunks = sorted(glob.glob(os.path.join(chunk_dir, "chunk_*.mp3")))
    if not chunks:
        raise RuntimeError(
            "ffmpeg produced no audio segments. Does the video contain an audio track?"
        )
    return chunks


def make_workdir() -> str:
    return tempfile.mkdtemp(prefix="videotranscriber_")


def cleanup(workdir: str) -> None:
    shutil.rmtree(workdir, ignore_errors=True)
