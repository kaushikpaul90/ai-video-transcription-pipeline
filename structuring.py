"""Transcript structuring — the Generative AI core of the pipeline.

For normal-length transcripts a single, well-prompted chat completion turns the raw
transcript into formatted Markdown. For very long transcripts (long videos) it would be
costly and could exceed the model context window to do this in one shot, so the module
automatically switches to a **map-reduce** strategy:

  * map    — structure each transcript chunk into Markdown sections + a few key points
             (in parallel);
  * reduce — synthesize one unified '## Summary' from just the per-chunk key points
             (a tiny, cheap call), then concatenate the structured sections.

This keeps cost bounded and predictable regardless of video length.
"""
from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Tuple

from config import Settings

SYSTEM_PROMPT = """You are an expert content editor. You convert raw, machine-generated
speech-to-text transcripts into clean, well-structured, reader-friendly documents.

Rules:
- Preserve the original meaning faithfully. Do NOT invent facts or add content that was
  not spoken. You may fix obvious transcription errors, punctuation, and capitalization.
- Organize the content into logical sections with clear Markdown headings (##).
- Use bullet points for lists, steps, key takeaways, and enumerations where appropriate.
- Start with a short '## Summary' section (3-5 bullets) capturing the key points.
- Keep paragraphs concise and scannable.
- Do not include speaker filler ("um", "uh", false starts) unless meaningful.
- Output valid Markdown only.
"""

USER_TEMPLATE = """Transform the following raw transcript into a well-structured Markdown
document following the rules.

After the document, add a final section exactly titled:
'## How This Was Organized'
containing 2-4 bullets briefly explaining the structure you chose.

RAW TRANSCRIPT:
\"\"\"
{transcript}
\"\"\"
"""

MAP_SYSTEM_PROMPT = """You are an expert content editor structuring ONE part of a longer
transcript. Faithfully preserve meaning; do not invent content. Fix punctuation and
obvious errors. Remove filler. Output valid Markdown only."""

MAP_USER_TEMPLATE = """This is part {index} of {total} of a transcript.

Return EXACTLY this format:

### Key Points
- (2-4 short bullets capturing the key points of THIS part)
### Content
(the structured Markdown for THIS part, using '##' / '###' headings and bullet points)

TRANSCRIPT PART:
\"\"\"
{chunk}
\"\"\"
"""

REDUCE_SYSTEM_PROMPT = """You merge key points from several parts of one document into a
single concise summary. Deduplicate and keep it faithful. Output Markdown bullets only."""

REDUCE_USER_TEMPLATE = """Combine the following key points (collected from sequential parts
of one transcript) into a single '## Summary' section of 4-7 deduplicated bullets that
captures the whole document. Output only the bullets (no heading).

KEY POINTS:
{key_points}
"""

ORG_NOTE = (
    "## How This Was Organized\n"
    "- The transcript was processed in sequential parts and each part was structured into "
    "topical sections with headings and bullet points.\n"
    "- Key points from every part were synthesized into a single deduplicated summary at "
    "the top.\n"
    "- Filler and false starts were removed while preserving the original meaning."
)


@dataclass
class StructuredResult:
    markdown: str


def _estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def _split_into_chunks(text: str, max_chars: int) -> List[str]:
    """Greedily pack sentences into chunks of at most ``max_chars`` characters."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    chunks: List[str] = []
    current = ""
    for sentence in sentences:
        if not sentence:
            continue
        if current and len(current) + len(sentence) + 1 > max_chars:
            chunks.append(current.strip())
            current = sentence
        elif len(sentence) > max_chars:
            # A single huge "sentence" (no punctuation) — hard-split it.
            if current:
                chunks.append(current.strip())
                current = ""
            for i in range(0, len(sentence), max_chars):
                chunks.append(sentence[i : i + max_chars].strip())
        else:
            current = f"{current} {sentence}".strip() if current else sentence
    if current.strip():
        chunks.append(current.strip())
    return chunks


def _chat(client, settings: Settings, system: str, user: str) -> str:
    response = client.chat.completions.create(
        model=settings.chat_deployment,
        temperature=0.2,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return (response.choices[0].message.content or "").strip()


def _parse_map_output(text: str) -> Tuple[str, str]:
    """Split a map response into (key_points, content)."""
    match = re.search(r"###\s*Content\s*\n", text)
    if not match:
        return "", text.strip()
    key_block = text[: match.start()]
    content = text[match.end() :].strip()
    key_points = re.sub(r"^\s*###\s*Key Points\s*\n", "", key_block, flags=re.IGNORECASE).strip()
    return key_points, content


def _structure_single(client, settings: Settings, transcript: str) -> str:
    return _chat(
        client,
        settings,
        SYSTEM_PROMPT,
        USER_TEMPLATE.format(transcript=transcript),
    )


def _process_chunk(args: tuple) -> tuple[int, str, str]:
    """Process a single chunk in the map phase. Returns (index, key_points, content)."""
    client, settings, i, total, chunk = args
    mapped = _chat(
        client,
        settings,
        MAP_SYSTEM_PROMPT,
        MAP_USER_TEMPLATE.format(index=i, total=total, chunk=chunk),
    )
    key_points, content = _parse_map_output(mapped)
    return i, key_points, content


def _structure_map_reduce(client, settings: Settings, transcript: str) -> str:
    chunks = _split_into_chunks(transcript, settings.structure_max_chars)
    print(f"      transcript is long -> map-reduce over {len(chunks)} part(s)")

    all_key_points: List[str] = []
    content_sections: List[str] = []
    results = {}

    # Adaptive parallelism: 4-6 workers depending on chunk count
    max_workers = min(max(4, len(chunks) // 2), 6)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_process_chunk, (client, settings, i, len(chunks), chunk)): i
            for i, chunk in enumerate(chunks, start=1)
        }

        for future in as_completed(futures):
            idx, key_points, content = future.result()
            results[idx] = (key_points, content)

    # Preserve order
    for i in sorted(results.keys()):
        key_points, content = results[i]
        if key_points:
            all_key_points.append(key_points)
        if content:
            content_sections.append(content)

    # Reduce: build one unified summary from just the (small) key points.
    if all_key_points:
        summary_bullets = _chat(
            client,
            settings,
            REDUCE_SYSTEM_PROMPT,
            REDUCE_USER_TEMPLATE.format(key_points="\n".join(all_key_points)),
        )
    else:
        summary_bullets = "- (summary unavailable)"

    parts = ["## Summary", summary_bullets, "", *content_sections, "", ORG_NOTE]
    return "\n".join(parts).strip()


def structure_transcript(client, settings: Settings, transcript: str) -> StructuredResult:
    if not transcript.strip():
        raise ValueError("Transcript is empty; nothing to structure.")

    if len(transcript) <= settings.structure_max_chars:
        markdown = _structure_single(client, settings, transcript)
    else:
        markdown = _structure_map_reduce(client, settings, transcript)

    return StructuredResult(markdown=markdown.strip())
