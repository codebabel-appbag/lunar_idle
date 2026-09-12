# Changelog

All notable changes to Lunar IDLE.

The format is based on Keep a Changelog, and this project adheres to
Semantic Versioning.

---

## [Unreleased]

Current state: functional.

### Project definition
- Lunar IDLE defined as a minimalist Lua IDE, inspired by Python's IDLE.
- Target: editor + REPL in tabs, single window, dark/light theme,
  configuration in a tab.
- Stack chosen: Python 3 + CustomTkinter (UI) + Tkinter (Text, Menu,
  Scrollbar, messagebox) + subprocess/PTY (REPL engine).

### Base modules
- `config.py` — preferences (`~/.lunar_config.json`), dark/light themes,
  editor and REPL fonts. Stable since first version.
- `highlighter.py` — Lua syntax highlighting via regex + `tk.Text` tags.
  Order: comment > string > keyword > number > function. Unchanged since
  first version.
- `editor.py` — Lua editor with line numbers, highlighting, Tab = 4 spaces,
  Shift+Tab unindent, vertical scrollbar synchronized with the gutter.
- `tabs.py` — IDE-style tab bar, supports `closable=False` (used by REPL and
  Configuration, which do not close via ✕).
- `main.py` — main window, menus, tab management, file open/save,
  Configuration tab.
- `repl.py` — interactive Lua REPL.

### REPL engine — from `lupa` to real `lua`

- The first version used `lupa` (Python-Lua bridge). Wrong tool:
  - `print` did not appear (buffering).
  - Errors mentioned Python, not Lua.
  - Hybrid behavior confused the user.
- Replaced with `subprocess.Popen(["lua", ...])` — real Lua, no middleman.
- **Problem that followed:** pipes buffered output and `lua` stayed silent
  until the process closed. Resolved with **PTY** (`pty.openpty()`), which
  makes `lua` behave as it does in a real terminal — no buffering.

### REPL — IDLE-style behavior

- Added `input_start` mark that isolates the editable line (only what comes
  after the `lua:: ` prompt).
- Backspace does not cross the prompt.
- Click before the prompt moves the cursor to the end.
- Key press before the prompt moves the cursor to the end.
- Filter for ANSI codes (`\x1b[?2004h`, etc.) and for the echo of `lua`'s
  native prompt.
- Auto-clean of the console when it reaches 100,000 characters.
- `shutdown()` closes the PTY `master_fd` and terminates the process
  gracefully.

### Configuration — from separate window to tab

- First version was a `Toplevel` (separate window). Problems:
  - Configuration did not actually apply.
  - Theme did not change.
  - Buttons disappeared.
  - Mixing `tk` and `ctk` caused bugs.
- Decision: move it to a **tab** inside the main window. Same widget tree,
  same theme context.
- The `Configuration` tab:
  - Has no ✕ (does not close by accident).
  - Title becomes `*Configuration` when there are unsaved changes.
  - `Save` button turns **green** when there are unsaved changes.
  - `Save` applies and closes the tab.
  - `Close` with unsaved changes → msgbox "Exit without saving?" →
    OK discards and closes / Cancel returns.
  - `Close` with no changes → closes directly.

### Theme

- `config.py` holds the dark/light themes.
- `main.py` applies the theme by iterating tabs + tab bar + menus.
- `ConfigTab.apply_theme` calls `ctk.set_appearance_mode("dark"/"light")`
  and explicitly reconfigures the `text_color` of labels — this is what
  made the theme actually apply.

### Main window

- Initial size 640x480, centered on screen.
- Menus: `File` (New, Open, Save, Save As, Exit), `Edit` (Undo, Redo, Cut,
  Copy, Paste), `Option` (Config), `Help` (About Lunar, Lunar Docs,
  Lua Docs).
- Shortcuts: Ctrl+N, Ctrl+O, Ctrl+S, Ctrl+Shift+S, Ctrl+W, Ctrl+Z, Ctrl+Y.

### REPL as a fixed tab

- No ✕, does not close.
- Title: `REPL ~ : Lua 5.3.6` (version detected via `lua -v`).
- When the application closes, the REPL is cleared and the `lua` process
  is terminated.

### Language

- Interface in **English** (conscious decision: accessible to the widest
  audience, standard in IDEs and editors).
- i18n (Simplified Chinese and others) documented as **roadmap / future
  contribution** — see `ROADMAP.md`.

### Current state

- `main.py` — functional, tested.
- `repl.py` — functional, real Lua REPL running via PTY.
  **Experimental:** the REPL behaves like a Lua terminal. Behavior may
  vary depending on the installed `lua` version and the platform.
- `editor.py`, `highlighter.py`, `tabs.py`, `config.py` — stable.

### Known issues

- `ConfigTab._on_save_click` calls `close_tab` before `apply_theme`. If it
  is not currently raising an error, it is due to timing luck — the race
  condition still exists.
- Multi-platform build (Linux/Windows/macOS) via PyInstaller + GitHub
  Actions — in preparation.
- Per-platform icons (`.png` for Linux, `.ico` for Windows, `.icns` for
  macOS) — in preparation.
- Per-platform metadata (`.desktop` + AppStream on Linux, version resource
  on Windows, `Info.plist` on macOS) — in preparation.