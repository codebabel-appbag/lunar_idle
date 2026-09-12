# Lunar IDLE — source layout

Technical overview of the source tree. For user-facing docs, see `docs/`.

---

## Layout

    lunar_idle/
    ├── main.py            # entry point, main window, menus, tabs
    ├── repl.py            # Lua REPL (PTY-based)
    ├── editor.py          # Lua editor widget
    ├── highlighter.py     # Lua syntax highlighting
    ├── tabs.py            # IDE-style tab bar
    ├── config.py          # preferences and themes
    ├── requirements.txt
    ├── README.md
    └── docs/
        ├── SKILL.md
        ├── CHANGELOG.md
        ├── ROADMAP.md
        └── USERMANUAL.md

---

## Module responsibilities

### `main.py`

Entry point. Defines:

- `Lunar(ctk.CTk)` — main window. Owns the menu bar, the tab bar, the
  tab registry (`self.tabs`), and the theme loop (`apply_theme`).
- `ConfigTab(ctk.CTkFrame)` — the Configuration tab.

Tab registry model:

    self.tabs = {
        tab_id: {
            "kind":   "repl" | "editor" | "config",
            "widget": <widget instance>,
            "path":   <str | None>,
            "title":  <str>
        }
    }

Two fixed tabs use reserved IDs:

- `self.repl_id` — the REPL tab (never closes).
- `self.config_tab_id` — the Configuration tab (never closes via ✕).

Run:

    python3 main.py

### `repl.py`

Interactive Lua REPL. Defines:

- `detect_lua_bin()` — searches `PATH` for a usable Lua binary in order:
  `lua`, `lua5.4`, `lua5.3`, `lua5.2`, `lua5.1`, `luajit`.
  Returns `(path, version_string)` or `(None, "unknown")`.
- `LuaREPL(tk.Frame)` — the REPL widget.

Execution model:

- `pty.openpty()` allocates a pseudo-terminal.
- `subprocess.Popen` runs the Lua binary with the PTY slave as
  stdin/stdout/stderr.
- A reader thread (`_read_pty_stream`) reads from the PTY master fd and
  hands data to the UI thread via `after()`.
- A `tk.Text` mark called `input_start` isolates the editable region
  (everything after the `lua:: ` prompt). Backspace, click, and key events
  are intercepted to prevent editing outside that region.
- ANSI escape codes are stripped with a compiled regex before insertion.
- Console auto-clears at `MAX_CHARS = 100_000`.
- `shutdown()` closes the PTY master fd and terminates the Lua process.

### `editor.py`

Lua editor widget. Defines:

- `LuaEditor(tk.Frame)` — a `tk.Text` with a `tk.Text` gutter (line
  numbers) and a `tk.Scrollbar`, all synchronized.

Public API:

- `get_code() -> str`
- `set_code(code: str) -> None`
- `apply_theme() -> None`

Bindings:

- `<Tab>` — insert 4 spaces.
- `<Shift-Tab>` — remove up to 4 spaces of leading indentation.
- `<KeyRelease>`, `<Configure>`, mouse wheel — trigger re-highlight and
  gutter redraw.

### `highlighter.py`

Lua syntax highlighting. Defines:

- `LUA_KEYWORDS` — list of Lua keywords.
- `TOKENS` — ordered list of `(tag, compiled_regex)` pairs. Order matters:
  comment > string > keyword > number > function.
- `apply_highlight(text_widget, theme)` — clears existing tags and
  re-applies them across the whole widget. Overlaps are avoided via an
  occupancy list so that, for example, a keyword inside a string is not
  re-tagged.

### `tabs.py`

IDE-style tab bar. Defines:

- `TabBar(tk.Frame)` — horizontal strip of tab buttons.

API:

- `add_tab(tab_id, title, closable=True)`
- `remove_tab(tab_id)`
- `set_active(tab_id)`
- `update_title(tab_id, title)`
- `is_closable(tab_id) -> bool`
- `apply_theme()`

The REPL and Configuration tabs are added with `closable=False`.

### `config.py`

Preferences. Persists to `~/.lunar_config.json`.

Defines:

- `DEFAULTS` — default values (theme, editor font/size, REPL font/size).
- `THEMES` — `"dark"` and `"light"` color dictionaries.
- `Config` — loaded at startup, merged with defaults, saved on `set()`.

Access:

    cfg.get("theme")        # "dark" | "light"
    cfg.set("theme", "light")
    cfg.theme               # property: returns the active theme dict

---

## Requirements

    customtkinter
    pyperclip

No other runtime dependency. The REPL depends on a system-provided `lua`
binary; it is not bundled.

---

## Running from source

    python3 -m venv .venv
    source .venv/bin/activate   # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    python3 main.py

---

## Platform notes

- Linux — full support. PTY and `lua` in `PATH` expected.
- macOS — expected to work the same way as Linux, provided a Lua binary
  is available (e.g. via Homebrew).
- Windows — the REPL relies on `pty`, which is not available natively on
  Windows. The application starts, but the REPL does not function without
  adaptation (WSL or a pipes-based fallback). Marked experimental.

---

## Where to go next

- `docs/SKILL.md` — full description of `main.py` and `repl.py`
  capabilities and limitations.
- `docs/CHANGELOG.md` — history of changes.
- `docs/ROADMAP.md` — planned features and i18n notes.
- `docs/USERMANUAL.md` — quick user-facing manual.