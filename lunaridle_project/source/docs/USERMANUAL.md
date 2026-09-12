# User Manual

A quick guide to using Lunar IDLE.

---

## Getting started

When you open Lunar IDLE, you are greeted with a single window containing
a fixed **REPL** tab. Everything happens in tabs: the REPL, editors, and
settings.

---

## The REPL

The REPL is always present — it never closes. It talks directly to your
system's `lua` binary.

- Type Lua code after the purple `lua:: ` prompt and press **Enter**.
- Output appears below, in real time.
- Errors appear in red.
- Past output is protected: you cannot edit it, only the current line.

Example:

    lua:: print("hello")
    hello
    lua:: local x = 10
    lua:: print(x * 2)
    20
    lua::

The REPL is **line-by-line**. Multi-line Lua blocks (`function ... end`)
may work if typed on a single line, but there is no block continuation
between lines.

---

## The Editor

### Opening a new editor

- Menu **File → New** (Ctrl+N).
- A new tab named `untitled` opens.

### Opening an existing file

- Menu **File → Open** (Ctrl+O).
- Choose a `.lua` file from the dialog.
- The file opens in a new tab, named after the file.

### Writing code

- Tab inserts 4 spaces.
- Shift+Tab removes 4 spaces of indentation.
- Line numbers are shown on the left.
- Lua syntax is highlighted automatically.

### Saving

- **Save** (Ctrl+S) — saves the current file.
  - If the file has never been saved, a save dialog opens
    (same as Save As).
- **Save As** (Ctrl+Shift+S) — always opens a save dialog.

The tab title changes to the file name once the file is saved.

### Closing an editor tab

- Click the **✕** on the tab.
- If the editor contains code, a confirmation dialog appears before
  closing.

---

## Configuration

Open **Option → Config** to open the `Configuration` tab.

You can change:

- **Theme** — Dark or Light.
- **Editor font** and **font size**.
- **REPL font** and **font size**.

Behavior:

- When you change any field, the tab title becomes `*Configuration` and
  the **Save** button turns green.
- Click **Save** to apply the changes and close the tab.
- Click **Close** with unsaved changes → a dialog asks
  "Exit without saving?". OK discards and closes; Cancel returns.
- Click **Close** with no changes → the tab closes directly.

The Configuration tab has no ✕ — it can only be closed with the
**Close** button.

---

## Menus at a glance

### File
- **New** (Ctrl+N) — new editor tab.
- **Open** (Ctrl+O) — open a `.lua` file.
- **Save** (Ctrl+S) — save the current editor.
- **Save As** (Ctrl+Shift+S) — save under a new name.
- **Exit** — close the application.

### Edit
- **Undo** (Ctrl+Z)
- **Redo** (Ctrl+Y)
- **Cut** (Ctrl+X)
- **Copy** (Ctrl+C)
- **Paste** (Ctrl+V)

Applies to the active widget (editor or REPL).

### Option
- **Config** — open the Configuration tab.

### Help
- **About Lunar** — application info.
- **Lunar Docs** — opens the repository in your browser.
- **Lua Docs** — opens the Lua 5.4 manual in your browser.

---

## Keyboard shortcuts

    Ctrl+N            New editor tab
    Ctrl+O            Open file
    Ctrl+S            Save
    Ctrl+Shift+S      Save As
    Ctrl+W            Close current editor tab
    Ctrl+Z            Undo
    Ctrl+Y            Redo
    Ctrl+X / C / V    Cut / Copy / Paste
    Enter             Run line in REPL
    Tab               Insert 4 spaces (editor)
    Shift+Tab         Remove 4 spaces of indentation (editor)

---

## Requirements

- Python 3.10+
- A Lua binary in your `PATH`:
  `lua`, `lua5.4`, `lua5.3`, `lua5.2`, `lua5.1`, or `luajit`.

If no Lua binary is found, the REPL will show "Lua nao disponivel." and
will not attempt to install one.

---

## Notes and limitations

- The REPL is **experimental**. It behaves like a Lua terminal. Behavior
  may vary depending on your Lua version and platform.
- On Windows, PTY is not available natively — the REPL does not work on
  Windows without adaptation.
- The interface is in English only. See `ROADMAP.md` for i18n plans.
- There is no find/replace, autocomplete, or session persistence yet.