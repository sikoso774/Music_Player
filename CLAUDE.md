# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

A desktop music player combining a VLC audio engine (via `python-vlc`/libVLC) with PySide6/Qt (for the GUI). Requires VLC to be installed on the machine (libVLC is loaded at runtime, not bundled).

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
2. If music was found, creates the `QApplication` and hands off to `src/gui/music_app_gui.py` (`MusicAppGUI`, a `QMainWindow`), which owns the rest of the app's lifetime via `app.exec()`. If none was found, the app prints a message and exits without opening any window. `MusicAppGUI` sets a `startup_failed` flag when it cannot start (VLC missing, empty playlist); `main.py` checks it and skips `show()`/`exec()` rather than opening a dead window.

### Package layout (`src/`)

- **`player/`** — audio engine, no UI dependencies beyond `python-vlc`:
  - `vlc_setup.py` — `create_vlc_player()`/`quit_vlc_player()`, returning and releasing a VLC `Instance`/`MediaPlayer` pair (held as `MusicPlayer` instance attributes, no module-level global state). `import vlc` is deliberately deferred inside `create_vlc_player()` so a missing libVLC surfaces as `VlcNotAvailableError` at a controlled point — after the GUI exists and can show a message — instead of crashing at import time.
  - `player_logic.py` — thin wrappers around the VLC `MediaPlayer` (load/play/pause/stop, direct seek via `set_time()`, volume, end-of-track detection via `get_state() == vlc.State.Ended`). `load_and_play()` briefly polls for the `Playing` state before seeking, since VLC's `play()` is asynchronous and an immediate `set_time()` can otherwise be dropped.
  - `audio_info.py` — uses `mutagen.File(path, easy=True)` (format auto-detection) to read duration/title/artist/album across any format mutagen supports, no per-format branching needed. Also the canonical home of the `AUDIO_FORMATS` tuple (imported by `search_musics.py`).
  - `music_player.py` — `MusicPlayer`, the stateful facade over the above. Tracks `current_track_index`, `is_playing`/`is_paused`. Unlike the old Pygame engine, VLC exposes an absolute playback position directly (`get_time()`/`set_time()`), so no manual position bookkeeping is needed — `seek_music()` seeks in place on an already-loaded track instead of reloading it. All playback/seek/next/prev operations funnel through here.
- **`gui/`** — PySide6 presentation layer, holds no playback state of its own:
  - `theme.py` — the neon palette constants (green/orange on near-black) *and* `build_stylesheet()`, which renders them into the app-wide QSS. Widgets are targeted by `objectName`, so this is the single place to change any color or widget style.
  - `gui_widgets.py` — the custom widgets (`NowPlayingWidget`, `ProgressWidget`, `ControlsWidget`, `VolumeWidget`, `PlaylistWidget`), each a self-contained `QWidget` exposing Qt signals. They render and emit; they never touch `MusicPlayer`.
  - `music_app_gui.py` — `MusicAppGUI` (a `QMainWindow`), the controller. Owns a `MusicPlayer`, connects the widgets' signals to it, and runs a `QTimer` polling loop to refresh the progress bar/labels and detect track-end.

  Qt gotchas the layout and the neon rendering depend on, all easy to reintroduce:
  - A bare `QWidget` ignores QSS `background-color`/`border` unless it sets `Qt.WA_StyledBackground` (unlike `QLabel`/`QPushButton`, which honor them natively).
  - `QLayout.SetFixedSize` pins a widget to its `sizeHint` and silently overrides any `setFixedWidth()` set alongside it. The window width is therefore imposed *from inside* the layout via `addStrut()`, and the same constraint is applied to the `QMainWindow`'s own layout — otherwise the window stays resizable and the content sits left-aligned with dead space beside it.
  - Under `SetFixedSize`, a non-wrapping `QLabel` with long text widens the whole window (its `sizeHint` is read before any elision happens). The now-playing labels use a horizontal `QSizePolicy.Ignored` and elide themselves in `resizeEvent`.
  - One `QGraphicsEffect` per widget, ever — setting a second silently replaces the first. Effects go on leaf widgets (an effect on a container flattens and blurs all its children together). Multi-layer halos are painted by hand in `paintEvent` with `CompositionMode_Plus` passes instead (`NeonSlider`, playlist delegate).
  - Enlarging a `QSlider` handle does not grow its `minimumSizeHint()` (stays 16 px); `NeonSlider` calls `setMinimumHeight()` or the handle/halo get clipped.
  - The transport glyphs `◀◀`/`▶▶`/`▮▮` are deliberate: `⏮`/`⏭`/`⏸` sit in a Unicode range Windows restyles into colored Fluent icons that override all styling.
- **`search_musics.py`** — `MusicFinder`, the one-shot startup music discovery step (see search order above). Not touched again after `main.py`'s setup phase.
- **`time_format.py`** — single shared `format_time(ms)` helper (MM:SS), used by both `player/` and `gui/` to avoid either package depending on the other.


### Legacy code

`others/` contains earlier iterations of this project (pre-refactor scripts) and is gitignored — not part of the active codebase.
