"""End-to-end orchestrator.

This is a deterministic, multi-step pipeline (NOT an autonomous agent loop):
    video -> extract audio -> chunk -> transcribe (STT) -> structure (Generative AI)
See APPROACH.md for the justification of this design choice.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass

import audio
import transcription
import structuring
from config import Settings, build_client


@dataclass
class PipelineOutput:
    raw_transcript: str
    structured_markdown: str
    raw_transcript_path: str
    structured_path: str


def run(video_path: str, output_dir: str = "output", keep_raw: bool = True) -> PipelineOutput:
    settings = Settings.load()
    client = build_client(settings)

    os.makedirs(output_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(video_path))[0]

    workdir = audio.make_workdir()
    try:
        print("[1/3] Extracting & segmenting audio with ffmpeg...")
        t_start = time.time()
        chunks = audio.extract_and_segment(
            video_path, workdir, settings.chunk_seconds, settings.audio_bitrate
        )
        print(f"      -> {len(chunks)} chunk(s) [{time.time() - t_start:.1f}s]")

        print("[2/3] Transcribing via Azure AI Foundry...")
        t_start = time.time()
        raw_transcript = transcription.transcribe(client, settings, chunks)
        print(f"      Done [{time.time() - t_start:.1f}s]")

        print("[3/3] Structuring transcript via Azure AI Foundry...")
        t_start = time.time()
        structured = structuring.structure_transcript(client, settings, raw_transcript)
        print(f"      Done [{time.time() - t_start:.1f}s]")
    finally:
        audio.cleanup(workdir)

    raw_path = os.path.join(output_dir, f"{base}.transcript.txt")
    structured_path = os.path.join(output_dir, f"{base}.structured.md")

    if keep_raw:
        with open(raw_path, "w", encoding="utf-8") as fh:
            fh.write(raw_transcript)
    with open(structured_path, "w", encoding="utf-8") as fh:
        fh.write(structured.markdown)

    return PipelineOutput(
        raw_transcript=raw_transcript,
        structured_markdown=structured.markdown,
        raw_transcript_path=raw_path,
        structured_path=structured_path,
    )
