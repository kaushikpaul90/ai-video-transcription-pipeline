"""Speech-to-text via an Azure AI Foundry transcription deployment (Whisper /
gpt-4o-transcribe). Each audio chunk is transcribed in parallel and the results are
concatenated in order to form the full raw transcript.
"""
from __future__ import annotations
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from typing import List
from config import Settings


def transcribe_chunk(client, deployment: str, chunk_path: str) -> tuple[int, str]:
    """Transcribe a single audio chunk and return its index and text."""
    path_parts = chunk_path.split("_")
    index = int(path_parts[-1].replace(".mp3", ""))
    
    with open(chunk_path, "rb") as fh:
        response = client.audio.transcriptions.create(
            model=deployment,
            file=fh,
            response_format="text",
        )
    # When response_format="text" the SDK returns a plain string.
    text = response if isinstance(response, str) else getattr(response, "text", str(response))
    return index, text


def transcribe(client, settings: Settings, chunk_paths: List[str]) -> str:
    """Transcribe all chunks in parallel and join them in order."""
    # Adaptive worker count: 6 for many chunks, capped at min(8, len(chunks))
    max_workers = min(max(4, len(chunk_paths) // 2), 8)
    results = {}
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(transcribe_chunk, client, settings.transcribe_deployment, path): i
            for i, path in enumerate(chunk_paths)
        }
        
        with tqdm(total=len(chunk_paths), desc="Transcribing", unit="chunk") as pbar:
            for future in as_completed(futures):
                index, text = future.result()
                results[index] = text.strip()
                pbar.update(1)
    
    parts = [results[i] for i in sorted(results.keys()) if results[i]]
    return "\n".join(parts).strip()
