# SKILL.md — Lunar IDLE capabilities

Full description of what Lunar IDLE can and cannot do, focused on the two
core modules: `main.py` (window, menus, tabs) and `repl.py` (Lua REPL).

---

# main.py — Window, menus, tabs

## Overview

`main.py` is the entry point of Lunar IDLE. It creates the main window,
the menu bar, the tab bar, and manages the entire lifecycle of tabs
(REPL, editor, configuration).

## What it CAN do

### Window
- Open at 640x480, centered on screen.
- Apply dark/light theme to itself, the container, the tab bar, the menus,
  and every live tab.
- Close by cleaning up the REPL (console + `lua` process) before destroying
  the window.

### Menus
- **File**
  - `New` (Ctrl+N) — open an empty editor tab (`untitled`).
  - `Open` (Ctrl+O) — file dialog, filters `.lua`, opens in a new tab.
  - `Save` (Ctrl+S) — saves the active editor. Falls back to Save As if
    no path is set.
  - `Save As` (Ctrl+Shift+S) — save dialog, sets the path.
  - `Exit` — closes the application.
- **Edit**
  - `Undo` (Ctrl+Z), `Redo` (Ctrl+Y), `Cut` (Ctrl+X), `Copy` (Ctrl+C),
    `Paste` (Ctrl+V) — applied to the active widget (editor or REPL).
- **Option**
  - `Config` — opens (or focuses) the `Configuration` tab.
- **Help**
  - `About Lunar` — msgbox with app info.
  - `Lunar Docs` — opens the repository in the browser.
  - `Lua Docs` — opens the Lua 5.4 manual in the browser.

### Tabs
- **REPL** — fixed, no close button, always present.
- **Editor** — opens via `New` or `Open`. Has a close button. Asks before
  closing if there is code.
- **Configuration** — fixed, no close button. Reopens if it already exists.

### Config (tab)
- Switch theme (Dark/Light).
- Set editor font and size.
- Set REPL font and size.
- Signal pending changes (`*Configuration` in the title, green `Save`).
- Save -> applies and closes.
- Close with pending changes -> asks.

## What it CANNOT do

- **No** multiple windows (single-window by design).
- **No** split view / side-by-side editors.
- **No** find/replace inside the editor.
- **No** smart auto-indent (only Tab = 4 spaces and Shift+Tab unindent).
- **No** syntax highlighting in the REPL (conscious decision: editor only).
- **No** command history with arrow keys in the REPL.
- **No** autocomplete.
- **No** session management (open tabs do not persist between runs).
- **No** i18n — interface is English-only (see ROADMAP.md).
- **No** context menu (right-click).
- **No** duplicate file detection.
- **No** Lua syntax validation before saving.

## Implementation details

- Class `Lunar(ctk.CTk)` — main window.
- Class `ConfigTab(ctk.CTkFrame)` — configuration tab.
- `self.tabs` — dict `{tab_id: {"kind", "widget", "path", "title"}}`.
- `self.repl_id` — REPL tab ID.
- `self.config_tab_id` — Configuration tab ID.
- Theme applied via `apply_theme()`, which iterates all tabs and calls
  `widget.apply_theme()` on any widget that has the method.

---

# repl.py — Lua REPL

## Overview

`repl.py` implements the Lua REPL of Lunar IDLE. It runs the system's real
`lua` binary as a subprocess, connected via **PTY** (pseudo-terminal), and
displays output in a `tk.Text` with behavior inspired by Python's IDLE.

WARNING: **Experimental.** The REPL behaves like an interactive Lua terminal.
Behavior may vary depending on your Lua version and platform.

## What it CAN do

- **Run real Lua** — no emulation, no bridge. The system's `lua` binary runs
  for real.
- **Detect the binary** — searches in order: `lua`, `lua5.4`, `lua5.3`,
  `lua5.2`, `lua5.1`, `luajit`. Extracts the version via `lua -v` to show
  in the tab title (`REPL ~ : Lua 5.3.6`).
- **Purple prompt** — `lua:: ` in bold. Theme-aware:
  - Dark: `#c586c0` (light purple)
  - Light: `#7c3aed` (dark purple)
- **`print` capture** — since `lua` is connected to a PTY, output appears
  in real time (no buffering).
- **Errors in red** — `lua` stderr is captured and shown in the theme's
  error color.
- **IDLE-style editing isolation**
  - Only the current line (after `lua:: `) is editable.
  - Backspace does not cross the prompt.
  - Click before the prompt moves the cursor to the end.
  - Key before the prompt moves the cursor to the end.
- **ANSI filter** — removes escape codes (e.g. `\x1b[?2004h`) that `lua`
  emits in PTY mode.
- **Auto-clean** — when the console reaches 100,000 characters, it is
  cleared, a warning message is inserted, and the prompt is rewritten.
- **Cleanup on close** — `clear()` is called by `main.py` when the
  application closes.
- **Clean shutdown** — `shutdown()` closes the PTY `master_fd` and
  terminates the `lua` process (with fallback to `kill`).

## What it CANNOT do

- **No** syntax highlighting (conscious decision: editor only).
- **No** command history with arrow keys.
- **No** autocomplete.
- **No** true multi-line — the REPL is line-by-line. Lua blocks
  (`function ... end`, `if ... then`) may work if typed on a single line,
  but there is no block continuation between lines.
- **No** support for Lua syntax that depends on multi-line terminal context
  (e.g. `=` in interactive `lua` mode, which prints expression values).
- **No** full emulation of `lua -i`. It is `lua` in pipe/PTY mode.
- **No** environment detection — if `lua` is not in `PATH`, it shows
  "Lua nao disponivel." and does not attempt installation.

## Implementation details

- Class `LuaREPL(tk.Frame)`.
- Engine via `pty.openpty()` + `subprocess.Popen([lua_path], stdin/stdout/stderr=slave_fd)`.
- Read in a **separate thread** (`_read_pty_stream`), sends output to the
  console via `after()` (thread-safe).
- Mark `input_start` isolates the editable line.
- `MAX_CHARS = 100_000` — auto-clean trigger.
- Regex `ANSI_ESCAPE` cleans escape codes.
- `.replace("> ", "").replace("\r", "")` removes echo of `lua`'s native
  prompt.

## Known limitations

- Depends on a `lua` binary installed on the system.
- On Windows, PTY does not exist natively — the REPL **does not work** on
  Windows without adaptation (use `pipes` as fallback, or WSL).
- Experience may vary depending on the `lua` version.