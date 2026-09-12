# Roadmap

Planned features, ideas, and future directions for Lunar IDLE.

This file is a living document. Nothing here is a promise — it is a
direction.

---

## Language and i18n

Lunar IDLE ships in **English** only. This is a conscious decision:

- English is the de facto standard in IDEs and editors (VS Code, Sublime,
  the official Lua tools, Python's own IDLE).
- It avoids maintaining N translation files for every string.
- It keeps the codebase simple and easy to contribute to.

### Future contribution: Simplified Chinese

Simplified Chinese (and other languages) is on the roadmap as a
**community contribution**. The technical path would be:

1. Extract strings into a translation file (`.po` via `gettext`, or a
   `.json`/own dict format).
2. Add locale detection (`LANG`/`LC_ALL`, or an option in `config.py`).
3. Fallback: if a key does not exist in the selected language, fall back
   to English.

This is **not implemented**. It is documented as an invitation to
contributors who want to add a language without the maintainer having to
carry it alone.

---

## Planned features

### Build and distribution

- Multi-platform build via PyInstaller + GitHub Actions
  (Linux, Windows, macOS).
- Per-platform icons:
  - Linux: `.png`
  - Windows: `.ico`
  - macOS: `.icns`
- Per-platform metadata:
  - Linux: `.desktop` file + AppStream metainfo
  - Windows: version resource embedded in the `.exe`
  - macOS: `Info.plist` inside the `.app` bundle

### REPL

- Command history with arrow keys (↑/↓).
- True multi-line support for Lua blocks (`function ... end`,
  `if ... then ... end`).
- Optional syntax highlighting in the REPL (currently editor-only by
  design).

### Editor

- Find and replace.
- Smarter auto-indent for Lua.
- Autocomplete for Lua keywords and builtins.

### Application

- Session persistence (reopen previously open tabs).
- Context menu (right-click).
- Duplicate file detection.
- Basic Lua syntax validation before saving.

---

## Non-goals

Things Lunar IDLE will **not** try to become:

- A full IDE like ZeroBrane Studio, EmmyLua, or VS Code + Lua extensions.
- A debugger.
- A project manager.
- A package manager.
- A Lua distribution (it will not ship the `lua` binary itself).
- An LSP client.

Lunar IDLE is a small, honest entry point for Lua — nothing more.

---

## Contributing

If you want to work on any item above, open an issue first to discuss the
approach. Small, focused pull requests are preferred.