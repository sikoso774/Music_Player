# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

A desktop music player combining a VLC audio engine (via `python-vlc`/libVLC) with CustomTkinter (for the GUI). Requires VLC to be installed on the machine (libVLC is loaded at runtime, not bundled).

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

Discovery is filtered by `AUDIO_FORMATS` in `src/player/audio_info.py`: `.mp3`, `.wav`, `.ogg`, `.opus`, `.flac`, `.m4a`, `.aac`, `.wma`, `.aiff`, `.aif`. Actual playback (VLC) and tag reading (`mutagen.File` auto-detection) support more than this list filters for — extend the tuple to widen discovery to other formats either supports.

## Architecture

Startup sequence in `main.py`:
1. `src/search_musics.py` (`MusicFinder`) — walks the filesystem for audio files (see search order above).
2. If music was found, builds the CustomTkinter root window and hands off to `src/gui/music_app_gui.py` (`MusicAppGUI`), which owns the rest of the app's lifetime via `root.mainloop()`. If none was found, the app prints a message and exits without opening any window.

### Package layout (`src/`)

- **`player/`** — audio engine, no UI dependencies beyond `python-vlc`:
  - `vlc_setup.py` — init/teardown of a module-level VLC `Instance`/`MediaPlayer` pair (`initialize_vlc_player()`/`quit_vlc_player()`), plus accessors (`get_media_player()`/`get_vlc_instance()`) used by `player_logic.py`.
  - `player_logic.py` — thin wrappers around the VLC `MediaPlayer` (load/play/pause/stop, direct seek via `set_time()`, volume, end-of-track detection via `get_state() == vlc.State.Ended`). `load_and_play()` briefly polls for the `Playing` state before seeking, since VLC's `play()` is asynchronous and an immediate `set_time()` can otherwise be dropped.
  - `audio_info.py` — uses `mutagen.File(path, easy=True)` (format auto-detection) to read duration/title/artist/album across any format mutagen supports, no per-format branching needed. Also the canonical home of the `AUDIO_FORMATS` tuple (imported by `search_musics.py`).
  - `music_player.py` — `MusicPlayer`, the stateful facade over the above. Tracks `current_track_index`, `is_playing`/`is_paused`. Unlike the old Pygame engine, VLC exposes an absolute playback position directly (`get_time()`/`set_time()`), so no manual position bookkeeping is needed — `seek_music()` seeks in place on an already-loaded track instead of reloading it. All playback/seek/next/prev operations funnel through here.
- **`gui/`** — CustomTkinter presentation layer, holds no playback state of its own:
  - `gui_elements.py` — pure widget-construction functions (labels, buttons, progress bar, playlist listbox). No logic, just layout. Also holds the copyright author/year defaults (`create_copyright_label`).
  - `gui_logic.py` — pure helper functions (`calculate_seek_position` for translating a progress-bar click into a track position; re-exports `format_time` from `src/time_format.py`).
  - `music_app_gui.py` — `MusicAppGUI`, the controller. Owns a `MusicPlayer` instance, wires widget callbacks to it, and runs a polling loop via `master.after(update_interval, ...)` to refresh the progress bar/labels and detect track-end.
- **`search_musics.py`** — `MusicFinder`, the one-shot startup music discovery step (see search order above). Not touched again after `main.py`'s setup phase.
- **`time_format.py`** — single shared `format_time(ms)` helper (MM:SS), used by both `player/` and `gui/` to avoid either package depending on the other.


### Legacy code

`others/` contains earlier iterations of this project (pre-refactor scripts) and is gitignored — not part of the active codebase.
