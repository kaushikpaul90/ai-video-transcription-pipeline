# VideoTranscriber

Ingest video files, generate accurate speech-to-text transcripts, and transform them
into well-structured, reader-friendly content. **All LLM/STT work runs on Azure AI
Foundry (Azure OpenAI).**

```
video  ─▶  extract & segment audio (ffmpeg, one-pass)
       ─▶  transcribe chunks (Whisper / gpt-4o-transcribe via Azure AI Foundry)
       ─▶  structure (Generative AI / gpt-4.1)  ─▶  output/*.structured.md
```

## Features
- Audio extraction from any ffmpeg-supported video (mp4, mov, mkv, ...).
- **Built for long videos:** a single streaming ffmpeg pass extracts + compresses +
  segments audio without loading it into memory, so multi-hour files work fine.
- Accurate STT via an Azure AI Foundry Whisper / `gpt-4o-transcribe` deployment.
- Generative-AI structuring into Markdown with **headings, bullet points, a summary**,
  and a short *"How This Was Organized"* note. Long transcripts use a **cost-bounded
  map-reduce** so context never overflows.
- **Cross-platform** (Windows / macOS / Linux) — pure ffmpeg + stdlib, no native audio libs.
- **Cost-conscious:** low-bitrate audio, cheapest-model defaults, one LLM call when the
  transcript fits, map-reduce only when it must.

## Cost & long-video notes
- **STT:** `whisper` is the cheapest transcription model; cost is per audio-minute.
- **Structuring:** uses `gpt-4.1` as the chat model.
- Audio is encoded to 32 kbps mono MP3 — a 1-hour video ≈ ~14 MB total, split into
  ~10-minute chunks well under the 25 MB STT limit.
- Transcripts under `STRUCTURE_MAX_CHARS` use a single LLM call (cheapest). Above it, the
  reduce step summarizes only the tiny per-chunk key points, keeping cost bounded.
- An 80-minute, 575 MB video was processed end-to-end in ~3 minutes with 9 audio chunks.

## Prerequisites
1. **Python 3.10+**
2. **ffmpeg** on your PATH — https://ffmpeg.org/download.html
   - Windows: `winget install Gyan.FFmpeg` — then **restart your terminal** so PATH is refreshed
   - macOS: `brew install ffmpeg`
   - Verify with: `ffmpeg -version`
3. An **Azure AI Foundry** resource with two deployments:
   - a transcription model (`whisper` or `gpt-4o-transcribe`)
   - a chat model (`gpt-4.1`, `gpt-4o-mini`, or `gpt-4o`)

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env   # Windows: copy .env.example .env
```

Edit `.env`:
- `AZURE_OPENAI_ENDPOINT` — e.g. `https://<resource>.openai.azure.com/`
- `AZURE_OPENAI_API_KEY` — leave blank to use Entra ID (`DefaultAzureCredential`)
- `AZURE_OPENAI_TRANSCRIBE_DEPLOYMENT` — your STT deployment name (`whisper` is cheapest)
- `AZURE_OPENAI_CHAT_DEPLOYMENT` — your chat deployment name (currently set to `gpt-4.1`)
- `AUDIO_CHUNK_SECONDS` / `AUDIO_BITRATE` — audio segmenting (defaults handle long videos)
- `STRUCTURE_MAX_CHARS` — transcript size above which structuring uses map-reduce

## Usage

```bash
# Basic run — outputs to ./output/
python main.py video.mp4

# Specify output directory
python main.py video.mp4 --output out

# Skip saving the raw transcript .txt
python main.py video.mp4 --no-keep-raw
```

Outputs land in `./output/`:
- `<name>.transcript.txt` — raw transcript (unless `--no-keep-raw`)
- `<name>.structured.md` — structured, formatted Markdown content

## Debugging in VS Code

A `.vscode/launch.json` is included with three debug configurations:

| Config | Description |
|--------|-------------|
| **VideoTranscriber: run video.mp4** | Full run with breakpoints — saves raw + structured output |
| **VideoTranscriber: run video.mp4 (no raw)** | Same, skips raw `.txt` file |
| **VideoTranscriber: current file** | Debug whatever Python file is currently open |

Set breakpoints in any module and press **F5** to launch.

## Project layout
| File | Responsibility |
|------|----------------|
| `config.py` | Settings + Foundry client (API key or Entra ID) |
| `audio.py` | One-pass ffmpeg extraction + low-bitrate MP3 segmentation |
| `transcription.py` | STT per chunk, ordered merge |
| `structuring.py` | **Generative AI** → structured Markdown (single-pass or map-reduce) |
| `pipeline.py` | Deterministic multi-step orchestrator |
| `main.py` | CLI entrypoint |

## Which AI approach? (and why)
**Chosen: an orchestrated multi-step pipeline with Generative AI at its core — not a
full autonomous Agentic system.** Full rationale in [`APPROACH.md`](./APPROACH.md).

> Short version: the workflow is fixed and deterministic (extract → transcribe →
> structure). There is no branching decision space that needs an autonomous agent, so a
> lightweight orchestrator + one well-prompted generative call gives the best accuracy,
> cost, latency, and maintainability. A clean seam in `structuring.py` lets you add an
> agentic layer later if requirements grow.
