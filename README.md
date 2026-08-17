# Music Player

A desktop music player combining a VLC audio engine with a PySide6/Qt GUI: loads audio files from a local folder and plays them with full transport controls.

## Features
- Load songs from a local folder
- Play, pause, skip, and seek (click or drag the progress bar) — seeking is instant, no reload of the file
- Display track/artist/album info, embedded album art, and playback progress
- Collapsible queue, with the window smoothly following its height
- Broad format support via VLC (mp3, wav, ogg, opus, flac, m4a, aac, wma, aiff, and more)

## Requirements
- Python >= 3.12
- [uv](https://docs.astral.sh/uv/) for dependency management
- [VLC media player](https://www.videolan.org/vlc/) installed on the machine (provides libVLC, loaded at runtime by `python-vlc`)
- Dependencies (see `pyproject.toml`): `python-vlc`, `PySide6`, `mutagen`, `pillow`

## Setup
1. Install [VLC](https://www.videolan.org/vlc/) if not already installed.
2. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) if not already installed.
3. Install dependencies:
   ```bash
   uv sync
   ```
4. Place audio files in a `Musiques` folder next to the project, or in your OS "Music" folder — the app searches both (see `CLAUDE.md` for the exact lookup order).

## Usage
```bash
uv run main.py
```

## Notes
- Audio *discovery* is filtered by `AUDIO_FORMATS` in `src/player/audio_info.py`: `.mp3`, `.wav`, `.ogg`, `.opus`, `.flac`, `.m4a`, `.aac`, `.wma`, `.aiff`, `.aif`. Actual playback (VLC) and tag reading (`mutagen`) support more than this list filters for.
- Track duration and tags (title/artist/album) are read via `mutagen`.
- Ensure audio files are accessible and not corrupted.
