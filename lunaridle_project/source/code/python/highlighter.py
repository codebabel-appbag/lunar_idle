# highlighter.py
import re
import tkinter as tk

LUA_KEYWORDS = [
    "and","break","do","else","elseif","end","false","for","function",
    "goto","if","in","local","nil","not","or","repeat","return","then",
    "true","until","while"
]

# ordem importa: comentário > string > keyword > número > função
TOKENS = [
    ("com",  re.compile(r"--\[\[.*?\]\]|--[^\n]*", re.DOTALL)),
    ("str",  re.compile(r"\[\[.*?\]\]|\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'", re.DOTALL)),
    ("kw",   re.compile(r"\b(?:" + "|".join(LUA_KEYWORDS) + r")\b")),
    ("num",  re.compile(r"\b\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\b|\b0[xX][0-9a-fA-F]+\b")),
    ("fn",   re.compile(r"\b[A-Za-z_]\w*(?=\s*\()")),
]

def apply_highlight(text_widget, theme):
    # limpa tags
    for tag in ("kw","str","com","num","fn"):
        text_widget.tag_remove(tag, "1.0", "end")

    content = text_widget.get("1.0", "end-1c")

    occupied = []  # evita overlap (ex: keyword dentro de string)
    def overlaps(a, b):
        for x, y in occupied:
            if not (b <= x or a >= y):
                return True
        return False

    for tag, pattern in TOKENS:
        for m in pattern.finditer(content):
            start, end = m.start(), m.end()
            if overlaps(start, end):
                continue
            occupied.append((start, end))
            i1 = f"1.0+{start}c"
            i2 = f"1.0+{end}c"
            text_widget.tag_add(tag, i1, i2)

    text_widget.tag_config("kw",  foreground=theme["kw"])
    text_widget.tag_config("str", foreground=theme["str"])
    text_widget.tag_config("com", foreground=theme["com"])
    text_widget.tag_config("num", foreground=theme["num"])
    text_widget.tag_config("fn",  foreground=theme["fn"])