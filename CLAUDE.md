# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

A desktop music player combining Pygame (for audio playback via `pygame.mixer`) with CustomTkinter (for the GUI). Pygame's window is only used at startup for a presentation splash screen; once the CustomTkinter GUI takes over, Pygame runs headless purely as the audio engine.

## Commands

This project uses `uv` for dependency management (Python >= 3.12).

```bash
# Install dependencies
uv sync

# Run the app
uv run main.py
```

There are no lint, format, or test configurations/commands in this repo.

## Music discovery

The app searches for playable audio in this order and uses the first non-empty result:
1. A `Musiques` folder next to the script/executable
2. The user's OS "Music" folder (`~/Music`)

Supported formats: `.mp3`, `.wav`, `.ogg`, `.flac`.

## Architecture

Startup sequence in `main.py`:
1. `pygame.init()`
2. `scripts/start_up/instructions.py` — prints CLI instructions/copyright text to the console.
3. `scripts/start_up/presentation.py` — shows a fading Pygame splash screen (image + author/project text), then fully closes the Pygame display via `pygame.display.quit()` before the GUI takes over (the audio mixer is a separate subsystem and keeps running).
4. `scripts/start_up/search_musics.py` (`MusicFinder`) — walks the filesystem for audio files (see search order above).
5. If music was found, builds the CustomTkinter root window and hands off to `scripts/gui/music_app_gui.py` (`MusicAppGUI`), which owns the rest of the app's lifetime via `root.mainloop()`.

### Package layout (`scripts/`)

- **`player/`** — audio engine, no UI dependencies beyond Pygame:
  - `pygame_setup.py` — init/teardown of `pygame.mixer` only (no display/window code).
  - `player_logic.py` — thin wrappers around `pygame.mixer.music` calls (load/play/pause/stop, position query).
  - `audio_info.py` — uses `mutagen` to read duration/title/artist/album per format (MP3/WAV/OGG/FLAC), with ID3-less-MP3 fallback. Also the canonical home of the `AUDIO_FORMATS` tuple (imported by `start_up/search_musics.py`).
  - `music_player.py` — `MusicPlayer`, the stateful facade over the above. Tracks `current_track_index`, `is_playing`/`is_paused`, and reconstructs elapsed playback time itself (`_start_position_ms_on_play` + Pygame's `get_pos()`) since Pygame doesn't expose absolute seek position. All playback/seek/next/prev operations funnel through here.
- **`gui/`** — CustomTkinter presentation layer, holds no playback state of its own:
  - `gui_elements.py` — pure widget-construction functions (labels, buttons, progress bar, playlist listbox). No logic, just layout.
  - `gui_logic.py` — pure helper functions (`calculate_seek_position` for translating a progress-bar click into a track position; re-exports `format_time` from `scripts/time_format.py`).
  - `music_app_gui.py` — `MusicAppGUI`, the controller. Owns a `MusicPlayer` instance, wires widget callbacks to it, and runs a polling loop via `master.after(update_interval, ...)` to refresh the progress bar/labels and detect track-end.
- **`start_up/`** — one-shot procedures run before the main GUI loop starts (instructions text, splash screen, music discovery). Not touched again after `main.py`'s setup phase.
- **`time_format.py`** — single shared `format_time(ms)` helper (MM:SS), used by both `player/` and `gui/` to avoid either package depending on the other.

### Key state-management detail

Pygame's mixer has no reliable "current absolute position" API when seeking mid-track — `MusicPlayer` compensates by remembering the position it started playback from (`_start_position_ms_on_play`) and adding Pygame's own `get_pos()` (time since that `play()` call). Any change to seek/play/pause logic must preserve this invariant or the progress bar and end-of-track detection will drift.

### Legacy code

`others/` contains earlier iterations of this project (pre-refactor scripts) and is gitignored — not part of the active codebase.
