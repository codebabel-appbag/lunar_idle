# Lunar IDLE

A minimalist Lua IDLE — editor and REPL in tabs, in a single window.

![Linux](https://img.shields.io/badge/Linux-supported-blue?logo=linux&logoColor=white)
![macOS](https://img.shields.io/badge/macOS-supported-black?logo=apple&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-experimental-orange?logo=windows&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Lua](https://img.shields.io/badge/Lua-5.1--5.4-2C2D72?logo=lua&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Welcome

Lunar IDLE is a small, focused IDE for Lua. It gives you two things in the same window: a real Lua REPL and a clean Lua editor. No plugins, no configuration wizard, no project scaffolding. Open it, write Lua, run Lua.

It was built for people who want the Python IDLE experience — but for Lua.

## What this project is

- A **minimalist IDE** for Lua.
- A **real REPL** that talks directly to your system's `lua` binary.
- An **editor** with line numbers, syntax highlighting and a synchronized scrollbar.
- A **single-window** application, with everything living in tabs.
- Part of the **minguanteEcossys** ecosystem — an effort to bring Lua back to life.

## What this project is NOT

To avoid ambiguity:

- It is **not** a full IDE like ZeroBrane Studio, EmmyLua or VS Code + Lua extensions. It does not have debugging, project management, LSP, or package management.
- It is **not** a Lua interpreter. It uses your system's `lua` binary.
- It is **not** a Lua distribution. It does not ship Lua itself.
- It is **not** a replacement for the official Lua interpreter or `luac`.
- It is **not** a library or a framework. It is an end-user application.

If you need a full-featured Lua IDE, this is not it. If you want something small, direct and honest, keep reading.

## Why another Lua IDLE?

Because Lua deserves a small, friendly entry point — the same way Python has IDLE. Lunar IDLE is that entry point. Nothing more, nothing less.

## Features

- **Real Lua REPL** — talks directly to `lua`, `lua5.4`, `lua5.3`, `lua5.2`, `lua5.1`, or `luajit`. No bridges, no emulation.
- **IDLE-inspired REPL behavior** — protected prompt, no editing of past output, no accidental overwrites.
- **Lua editor** — line numbers, syntax highlighting, Tab = 4 spaces, synchronized scrollbar.
- **Tabs** — REPL, editor and settings all in the same window.
- **Dark / Light theme.**
- **Configurable fonts** — separately for editor and REPL.
- **Settings in a tab** — no modal windows.

## Documentation

Full documentation lives in the `docs/` folder:
- `docs/` [docs/](https://github.com/codebabel-appbag/lunar_idle/tree/main/lunaridle_project/source/docs)
- `docs/SKILL.md` [SKILL.md](https://github.com/codebabel-appbag/lunar_idle/blob/main/lunaridle_project/source/docs/SKILL.md) — what the app can and cannot do (`main.py` and `repl.py` in detail).
- `docs/CHANGELOG.md` [CHANGELOG.md](https://github.com/codebabel-appbag/lunar_idle/blob/main/lunaridle_project/source/docs/CHANGELOG.md) — history of changes.
- `docs/ROADMAP.md` [ROADMAP.md](https://github.com/codebabel-appbag/lunar_idle/blob/main/lunaridle_project/source/docs/ROADMAP.md) — planned features and i18n notes.
- `docs/USERMANUAL.md` [USERMANUAL.md](https://github.com/codebabel-appbag/lunar_idle/blob/main/lunaridle_project/source/docs/USERMANUAL.md) — easy user manual.

## Installation

    git clone https://github.com/codebabel-appbag/lua/lunar_idle.git
    cd lunar_idle
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    python3 main.py

## License

MIT © codebabel

---

<sub>Part of the **minguanteEcossys** ecosystem — bringing Lua back to life.</sub>
