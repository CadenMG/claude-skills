#!/usr/bin/env python3
"""
Fetch the transcript of a YouTube video.

Usage:
    python fetch_transcript.py <video_id_or_url> [--lang LANG] [--format FORMAT]

Arguments:
    video_id_or_url   YouTube video ID (e.g. dQw4w9WgXcQ) or full URL
    --lang            Preferred language code (default: en). Falls back to any available.
    --format          Output format: text (default), json, srt

Dependencies:
    pip install youtube-transcript-api
"""

import argparse
import json
import re
import sys


def extract_video_id(input_str: str) -> str:
    """Extract video ID from a URL or return as-is if already an ID."""
    patterns = [
        r"(?:v=|youtu\.be/|embed/|shorts/)([A-Za-z0-9_-]{11})",
        r"^([A-Za-z0-9_-]{11})$",
    ]
    for pattern in patterns:
        match = re.search(pattern, input_str)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract video ID from: {input_str!r}")


def fetch_transcript(video_id: str, lang: str = "en"):
    try:
        from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
    except ImportError:
        print("Error: youtube-transcript-api is not installed.", file=sys.stderr)
        print("Install it with: pip install youtube-transcript-api", file=sys.stderr)
        sys.exit(1)

    api = YouTubeTranscriptApi()
    transcript_list = api.list(video_id)

    # Try preferred language first, then any manually created, then any generated
    try:
        transcript = transcript_list.find_transcript([lang])
    except NoTranscriptFound:
        try:
            # Fall back to any manually created transcript
            transcript = transcript_list.find_manually_created_transcript(
                [t.language_code for t in transcript_list]
            )
        except NoTranscriptFound:
            # Fall back to any auto-generated transcript
            transcript = transcript_list.find_generated_transcript(
                [t.language_code for t in transcript_list]
            )

    fetched = transcript.fetch()
    entries = [{"text": s.text, "start": s.start, "duration": s.duration} for s in fetched]
    return entries, transcript.language, transcript.language_code


def format_as_text(entries) -> str:
    return " ".join(entry["text"].strip() for entry in entries)


def format_as_srt(entries) -> str:
    lines = []
    for i, entry in enumerate(entries, start=1):
        start = entry["start"]
        end = start + entry.get("duration", 2.0)
        lines.append(str(i))
        lines.append(f"{_srt_time(start)} --> {_srt_time(end)}")
        lines.append(entry["text"].strip())
        lines.append("")
    return "\n".join(lines)


def _srt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def main():
    parser = argparse.ArgumentParser(description="Fetch YouTube video transcript")
    parser.add_argument("video", help="YouTube video ID or URL")
    parser.add_argument("--lang", default="en", help="Preferred language code (default: en)")
    parser.add_argument(
        "--format",
        choices=["text", "json", "srt"],
        default="text",
        help="Output format (default: text)",
    )
    args = parser.parse_args()

    try:
        video_id = extract_video_id(args.video)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        entries, language, language_code = fetch_transcript(video_id, args.lang)
    except Exception as e:
        print(f"Error fetching transcript: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"# Transcript — video_id={video_id}  language={language} ({language_code})\n", file=sys.stderr)

    if args.format == "json":
        print(json.dumps(entries, indent=2, ensure_ascii=False))
    elif args.format == "srt":
        print(format_as_srt(entries))
    else:
        print(format_as_text(entries))


if __name__ == "__main__":
    main()
