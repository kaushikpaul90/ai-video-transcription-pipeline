"""Configuration and Azure AI Foundry (Azure OpenAI) client construction.

Supports two auth modes:
  * API key  -> set AZURE_OPENAI_API_KEY
  * Entra ID -> leave the key blank; DefaultAzureCredential is used.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    endpoint: str
    api_key: str | None
    api_version: str
    transcribe_deployment: str
    chat_deployment: str
    chunk_seconds: int
    audio_bitrate: str
    structure_max_chars: int

    @staticmethod
    def load() -> "Settings":
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
        if not endpoint:
            raise RuntimeError(
                "AZURE_OPENAI_ENDPOINT is not set. Copy .env.example to .env and fill it in."
            )
        return Settings(
            endpoint=endpoint,
            api_key=(os.getenv("AZURE_OPENAI_API_KEY") or "").strip() or None,
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview").strip(),
            transcribe_deployment=os.getenv(
                "AZURE_OPENAI_TRANSCRIBE_DEPLOYMENT", "whisper"
            ).strip(),
            chat_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o").strip(),
            chunk_seconds=int(os.getenv("AUDIO_CHUNK_SECONDS", "900")),
            audio_bitrate=os.getenv("AUDIO_BITRATE", "32k").strip(),
            structure_max_chars=int(os.getenv("STRUCTURE_MAX_CHARS", "48000")),
        )


def build_client(settings: Settings):
    """Return an AzureOpenAI client wired to the Foundry deployment.
    
    The client is efficiently reused across multiple API calls with connection
    pooling and persistent credentials to minimize overhead.
    """
    from openai import AzureOpenAI

    if settings.api_key:
        return AzureOpenAI(
            azure_endpoint=settings.endpoint,
            api_key=settings.api_key,
            api_version=settings.api_version,
            timeout=60.0,
            max_retries=2,
        )

    # Entra ID auth (no key) via DefaultAzureCredential.
    from azure.identity import DefaultAzureCredential, get_bearer_token_provider

    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
    )
    return AzureOpenAI(
        azure_endpoint=settings.endpoint,
        azure_ad_token_provider=token_provider,
        api_version=settings.api_version,
        timeout=60.0,
        max_retries=2,
    )
