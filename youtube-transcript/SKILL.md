---
name: youtube-transcript
description: This skill should be used when the user asks to "get the transcript" of a YouTube video, "fetch subtitles" from YouTube, "summarize a YouTube video", "transcribe a YouTube video", or provides a YouTube URL and wants to read, analyze, or work with its spoken content.
version: 1.0.0
---

# YouTube Transcript Skill

Fetch and work with the transcript (captions/subtitles) of any YouTube video using a bundled Python script backed by the `youtube-transcript-api` library.

## When to Use

Apply this skill whenever the user supplies a YouTube video ID or URL and wants to:

- Read or display the transcript
- Summarize, analyze, or extract information from the video's spoken content
- Convert captions to a different format (plain text, SRT, JSON)
- Translate or process subtitles programmatically

## Dependencies

The script requires one third-party package:

```bash
pip install youtube-transcript-api
```

Check whether it is already installed before prompting the user to install it:

```bash
python -c "import youtube_transcript_api" 2>/dev/null && echo "installed" || echo "missing"
```

## Fetching a Transcript

Use `scripts/fetch_transcript.py` (path relative to this skill directory):

```bash
python <skill-dir>/scripts/fetch_transcript.py <video_id_or_url> [--lang LANG] [--format FORMAT]
```

### Arguments

| Argument | Description | Default |
|---|---|---|
| `video_id_or_url` | 11-char video ID or any YouTube URL form | (required) |
| `--lang` | Preferred language code (e.g. `en`, `es`, `fr`) | `en` |
| `--format` | Output format: `text`, `json`, `srt` | `text` |

### Examples

```bash
# Plain text transcript (default)
python fetch_transcript.py dQw4w9WgXcQ

# From a full URL
python fetch_transcript.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Spanish subtitles in SRT format
python fetch_transcript.py dQw4w9WgXcQ --lang es --format srt

# Structured JSON (includes start time and duration per segment)
python fetch_transcript.py dQw4w9WgXcQ --format json
```

The script prints a one-line header to stderr (video ID and detected language) and the transcript to stdout, so stderr and stdout can be separated if needed.

## Language Fallback Behavior

1. Try the requested `--lang` code exactly.
2. Fall back to any manually-created transcript available for the video.
3. Fall back to any auto-generated (ASR) transcript.
4. If nothing is available, the script exits with an error.

Use `--format json` to inspect raw segment data (start times, durations) when the user needs timestamped captions.

## Common Failure Modes

| Error | Likely Cause | Fix |
|---|---|---|
| `TranscriptsDisabled` | Video owner disabled captions | No workaround via this API |
| `NoTranscriptFound` | Requested language not available | Try a different `--lang` or omit it to auto-select |
| `VideoUnavailable` | Video is private, deleted, or region-locked | Confirm the video is publicly accessible |
| `ImportError` | Package not installed | Run `pip install youtube-transcript-api` |

## Workflow

1. Extract or confirm the video ID from the user-provided URL.
2. Run the script with the appropriate flags.
3. Pipe stdout into further processing (summarization, translation, search) as needed.
4. If an error occurs, read the stderr message and apply the fix from the table above before retrying.
