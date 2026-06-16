"""Audio extraction and chunking for long videos (cross-platform: Windows/macOS/Linux).

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
from urllib.parse import urlparse


def _require_ffmpeg() -> None:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "ffmpeg was not found on PATH. Install it (https://ffmpeg.org/download.html) "
            "and ensure 'ffmpeg' is runnable from a terminal.\n"
            "  Windows: winget install Gyan.FFmpeg   |   macOS: brew install ffmpeg"
        )


def _is_url(input_str: str) -> bool:
    """Check if input is a URL (YouTube or other media URL)."""
    try:
        result = urlparse(input_str)
        return result.scheme in ("http", "https")
    except Exception:
        return False


def _download_video(url: str, workdir: str) -> str:
    """Download video from URL (YouTube, etc.) using yt-dlp.
    
    Returns the path to the downloaded video file.
    """
    try:
        import yt_dlp
    except ImportError:
        raise RuntimeError(
            "yt-dlp is required to download videos from URLs. "
            "Install it with: pip install yt-dlp"
        )
    
    output_path = os.path.join(workdir, "downloaded_video.%(ext)s")
    
    ydl_opts = {
        "format": "best[ext=mp4]/best[ext=webm]/best",
        "outtmpl": output_path,
        "quiet": False,
        "no_warnings": False,
    }
    
    print(f"  Downloading video from {url}...")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            downloaded_file = ydl.prepare_filename(info)
            print(f"  Downloaded: {downloaded_file}")
            return downloaded_file
    except Exception as e:
        raise RuntimeError(f"Failed to download video from {url}: {str(e)}")


def _resolve_video_path(video_input: str, workdir: str) -> str:
    """Resolve video input: download if URL, otherwise resolve file path.
    
    Returns the resolved local file path.
    """
    if _is_url(video_input):
        return _download_video(video_input, workdir)
    
    resolved_path = video_input
    if not os.path.isfile(resolved_path):
        data_path = os.path.join(os.getcwd(), "data", video_input)
        if os.path.isfile(data_path):
            resolved_path = data_path
        else:
            raise FileNotFoundError(
                f"Video file not found: {video_input}\n"
                f"  Checked: {video_input} and data/{video_input}"
            )
    
    return resolved_path


def extract_and_segment(
    video_path: str,
    workdir: str,
    chunk_seconds: int,
    bitrate: str = "32k",
) -> List[str]:
    """Extract audio and split it into <= chunk_seconds MP3 segments in one ffmpeg pass.

    Accepts both local file paths and URLs (YouTube, etc.).
    Returns an ordered list of chunk file paths. Short videos yield a single chunk.
    Uses optimized libmp3lame settings for faster encoding.
    """
    _require_ffmpeg()
    
    # Resolve video path: download if URL, otherwise use local file
    video_input = _resolve_video_path(video_path, workdir)

    chunk_dir = os.path.join(workdir, "chunks")
    os.makedirs(chunk_dir, exist_ok=True)
    pattern = os.path.join(chunk_dir, "chunk_%04d.mp3")

    cmd = [
        "ffmpeg", "-y",
        "-i", video_input,
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
