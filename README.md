# Pygame Music Player

A desktop music player combining a Pygame audio engine with a CustomTkinter GUI: loads audio files from a local folder and plays them with full transport controls.

## Features
- Load songs from a local folder
- Play, pause, skip, and seek (click or drag the progress bar)
- Display track/artist/album info and playback progress in a CustomTkinter GUI (Pygame runs headless as the audio engine only — no visible Pygame window once the app is up)

## Requirements
- Python >= 3.12
- [uv](https://docs.astral.sh/uv/) for dependency management
- Dependencies (see `pyproject.toml`): `pygame-ce`, `customtkinter`, `mutagen`, `pillow`

## Setup
1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) if not already installed.
2. Install dependencies:
   ```bash
   uv sync
   ```
3. Place audio files in a `Musiques` folder next to the project, or in your OS "Music" folder — the app searches both (see `CLAUDE.md` for the exact lookup order).

## Usage
```bash
uv run main.py
```

## Notes
- Supported audio formats are filtered by `AUDIO_FORMATS` in `src/player/audio_info.py`: `.mp3`, `.wav`, `.ogg`, `.flac`.
- Track duration and tags (title/artist/album) are read via `mutagen`.
- Ensure audio files are accessible and not corrupted.
