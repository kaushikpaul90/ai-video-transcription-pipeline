"""Speech-to-text via an Azure AI Foundry transcription deployment (Whisper /
gpt-4o-transcribe). Each audio chunk is transcribed and the results are concatenated
in order to form the full raw transcript.
"""
from __future__ import annotations
from tqdm import tqdm
from typing import List
from config import Settings


def transcribe_chunk(client, deployment: str, chunk_path: str) -> str:
    """Transcribe a single audio chunk and return its text."""
    with open(chunk_path, "rb") as fh:
        response = client.audio.transcriptions.create(
            model=deployment,
            file=fh,
            response_format="text",
        )
    # When response_format="text" the SDK returns a plain string.
    return response if isinstance(response, str) else getattr(response, "text", str(response))


def transcribe(client, settings: Settings, chunk_paths: List[str]) -> str:
    """Transcribe all chunks in order and join into one transcript."""
    parts: List[str] = []
    for path in tqdm(chunk_paths, desc="Transcribing", unit="chunk"):
        text = transcribe_chunk(client, settings.transcribe_deployment, path).strip()
        if text:
            parts.append(text)
    return "\n".join(parts).strip()
