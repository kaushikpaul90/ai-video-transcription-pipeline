# VideoTranscriber

Ingest video files **or YouTube URLs**, generate accurate speech-to-text transcripts, and transform them
into well-structured, reader-friendly content. **All LLM/STT work runs on Azure AI
Foundry (Azure OpenAI).**

```
video /        download (       extract & segment audio (ffmpeg, one-pass)if URL) YouTube URL  
       transcribe chunks (Whisper / gpt-4o-transcribe via Azure AI Foundry)                     
       structure (Generative AI / gpt-       output/*.structured.md4.1)                       
```

## Features
- **Local files or YouTube URLs:** pass a file path or YouTube  it just works.link 
- Audio extraction from any ffmpeg-supported video (mp4, mov, mkv, ...).
- **Built for long videos:** a single streaming ffmpeg pass extracts + compresses +
  segments audio without loading it into memory, so multi-hour files work fine.
- Accurate STT via an Azure AI Foundry Whisper / `gpt-4o-transcribe` deployment.
- Generative-AI structuring into Markdown with **headings, bullet points, a summary**,
  and a short *"How This Was Organized"* note. Long transcripts use a **cost-bounded
  map-reduce** so context never overflows.
- **Cross-platform** (Windows / macOS /  pure ffmpeg + stdlib, no native audio libs.Linux) 
- **Cost-conscious:** low-bitrate audio, cheapest-model defaults, one LLM call when the
  transcript fits, map-reduce only when it must.

## Cost & long-video notes
- **STT:** `whisper` is the cheapest transcription model; cost is per audio-minute.
- **Structuring:** uses `gpt-4.1` as the chat model.
- Audio is encoded to 32 kbps mono  a 1- ~14 MB total, split intovideo MP3 
  ~10-minute chunks well under the 25 MB STT limit.
- Transcripts under `STRUCTURE_MAX_CHARS` use a single LLM call (cheapest). Above it, the
  reduce step summarizes only the tiny per-chunk key points, keeping cost bounded.
- An 80-minute, 575 MB video was processed end-to-end in ~3 minutes with 9 audio chunks.

## Prerequisites
1. **Python 3.10+**
2. **ffmpeg** on your  https://ffmpeg.org/download.htmlPATH 
   - Windows: `winget install Gyan. then **restart your terminal** so PATH is refreshedFFmpeg` 
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
- `AZURE_OPENAI_ e.g. `https://<resource>.openai.azure.com/`ENDPOINT` 
- `AZURE_OPENAI_API_ leave blank to use Entra ID (`DefaultAzureCredential`)KEY` 
- `AZURE_OPENAI_TRANSCRIBE_ your STT deployment name (`whisper` is cheapest)DEPLOYMENT` 
- `AZURE_OPENAI_CHAT_ your chat deployment name (currently set to `gpt-4.1`)DEPLOYMENT` 
- `AUDIO_CHUNK_SECONDS` / `AUDIO_ audio segmenting (defaults handle long videos)BITRATE` 
- `STRUCTURE_MAX_ transcript size above which structuring uses map-reduceCHARS` 

## Usage

```bash
# Local video  outputs to ./output/file 
python main.py video.mp4

# YouTube URL (or any media URL)
python main.py https://www.youtube.com/watch?v=dQw4w9WgXcQ

# Specify output directory
python main.py video.mp4 --output out

# Skip saving the raw transcript .txt
python main.py video.mp4 --no-keep-raw
```

Outputs land in `./output/`:
- `<name>.transcript. raw transcript (unless `--no-keep-raw`)txt` 
- `<name>.structured. structured, formatted Markdown contentmd` 

### YouTube & Media URLs
When you pass a URL, the application:
1. Downloads the video automatically using `yt-dlp` (works with YouTube, Vimeo, and 1000+ other sites)
2. Extracts audio and continues the normal pipeline
3. Cleans up the downloaded file after processing

No additional setup  just pass the URL!needed 

## Debugging in VS Code

A `.vscode/launch.json` is included with three debug configurations:

| Config | Description |
|--------|-------------|
| **VideoTranscriber: run video.mp4** | Full run with  saves raw + structured output |breakpoints 
| **VideoTranscriber: run video.mp4 (no raw)** | Same, skips raw `.txt` file |
| **VideoTranscriber: current file** | Debug whatever Python file is currently open |

Set breakpoints in any module and press **F5** to launch.

## Project layout
| File | Responsibility |
|------|----------------|
| `config.py` | Settings + Foundry client (API key or Entra ID) |
| `audio.py` | URL download, one-pass ffmpeg extraction + low-bitrate MP3 segmentation |
| `transcription.py` | STT per chunk, ordered merge |
 structured Markdown (single-pass or map-reduce) |
| `pipeline.py` | Deterministic multi-step orchestrator |
| `main.py` | CLI entrypoint |

## Which AI approach? (and why)
**Chosen: an orchestrated multi-step pipeline with Generative AI at its  not acore 
full autonomous Agentic system.** Full rationale in [`APPROACH.md`](./APPROACH.md).


> structure). There is no branching decision space that needs an autonomous agent, so a
> lightweight orchestrator + one well-prompted generative call gives the best accuracy,
> cost, latency, and maintainability. A clean seam in `structuring.py` lets you add an
> agentic layer later if requirements grow.
