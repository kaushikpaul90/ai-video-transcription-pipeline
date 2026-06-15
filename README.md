# VideoTranscriber

Ingest video files, generate accurate speech-to-text transcripts, and transform them
into well-structured, reader-friendly content. **All LLM/STT work runs on Azure AI
Foundry (Azure OpenAI).**

```
video  ─▶  extract audio (ffmpeg)  ─▶  chunk  ─▶  transcribe (Whisper / gpt-4o-transcribe)
       ─▶  structure (Generative AI / gpt-4o)  ─▶  output/*.structured.md
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
- **Structuring:** defaults to `gpt-4o-mini` (~15-20× cheaper than `gpt-4o`).
- Audio is encoded to 32 kbps mono MP3 — a 1-hour video ≈ ~14 MB total, split into
  ~15-minute chunks well under the 25 MB STT limit.
- Transcripts under `STRUCTURE_MAX_CHARS` use a single LLM call (cheapest). Above it, the
  reduce step summarizes only the tiny per-chunk key points, keeping cost bounded.

## Prerequisites
1. **Python 3.10+**
2. **ffmpeg** on your PATH — https://ffmpeg.org/download.html
3. An **Azure AI Foundry** resource with two deployments:
   - a transcription model (`whisper` or `gpt-4o-transcribe`)
   - a chat model (`gpt-4o` or `gpt-4o-mini`)

## Setup
```bash
pip install -r requirements.txt
cp .env.example .env        # then fill in your Foundry values
```

Edit `.env`:
- `AZURE_OPENAI_ENDPOINT` — e.g. `https://<resource>.openai.azure.com/`
- `AZURE_OPENAI_API_KEY` — leave blank to use Entra ID
- `AZURE_OPENAI_TRANSCRIBE_DEPLOYMENT` — your STT deployment name (`whisper` is cheapest)
- `AZURE_OPENAI_CHAT_DEPLOYMENT` — your chat deployment name (`gpt-4o-mini` is cheapest)
- `AUDIO_CHUNK_SECONDS` / `AUDIO_BITRATE` — audio segmenting (defaults handle long videos)
- `STRUCTURE_MAX_CHARS` — transcript size above which structuring uses map-reduce

## Usage
```bash
python main.py path/to/video.mp4
python main.py path/to/video.mp4 --output out --no-keep-raw
```

Outputs land in `./output/`:
- `<name>.transcript.txt` — raw transcript (unless `--no-keep-raw`)
- `<name>.structured.md` — structured, formatted content

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

## Notes
- This repo ships runnable code + docs. It was authored in an environment without a
  shell, so it has not been executed here — run the setup steps above to use it.
