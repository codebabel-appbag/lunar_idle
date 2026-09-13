# editor.py(v2)
import tkinter as tk
from highlighter import apply_highlight


class LuaEditor(tk.Frame):
    def __init__(self, master, cfg):
        super().__init__(master)
        self.cfg = cfg
        t = cfg.theme

        # container interno pra alinhar gutter + text + scrollbar
        self.text = tk.Text(
            self, wrap="none", undo=True,
            bg=t["bg"], fg=t["fg"],
            insertbackground=t["cursor"],
            selectbackground=t["select"],
            relief="flat", borderwidth=0,
            font=(cfg.get("editor_font"), cfg.get("editor_size")),
            padx=6, pady=4,
        )
        self.gutter = tk.Text(
            self, width=4, padx=4, takefocus=0,
            bg=t["gutter_bg"], fg=t["gutter_fg"],
            relief="flat", borderwidth=0,
            font=(cfg.get("editor_font"), cfg.get("editor_size")),
            state="disabled",
        )
        self.scroll = tk.Scrollbar(
            self, orient="vertical", command=self._on_scroll,
            bg=t["bg"], troughcolor=t["gutter_bg"],
            activebackground=t["select"], relief="flat", borderwidth=0,
        )

        self.gutter.pack(side="left", fill="y")
        self.scroll.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)

        # sincroniza text <-> scrollbar
        self.text.configure(yscrollcommand=self._on_yscroll)

        self.text.bind("<KeyRelease>", self._refresh)
        self.text.bind("<MouseWheel>", self._sync_scroll, add="+")
        self.text.bind("<Button-4>", self._sync_scroll, add="+")
        self.text.bind("<Button-5>", self._sync_scroll, add="+")
        self.text.bind("<Configure>", lambda e: self._refresh())
        self.text.bind("<Tab>", self._insert_tab)
        self.text.bind("<Shift-Tab>", self._unindent)

        self._refresh()

    # ---------- scroll ----------
    def _on_scroll(self, *args):
        self.text.yview(*args)
        self.gutter.yview(*args)

    def _on_yscroll(self, first, last):
        self.scroll.set(first, last)
        self.gutter.yview_moveto(first)

    def _sync_scroll(self, event=None):
        try:
            self.gutter.yview_moveto(self.text.yview()[0])
            self.scroll.set(*self.text.yview())
        except Exception:
            pass

    # ---------- refresh ----------
    def _refresh(self, event=None):
        apply_highlight(self.text, self.cfg.theme)
        self._redraw_gutter()

    def _redraw_gutter(self):
        self.gutter.config(state="normal")
        self.gutter.delete("1.0", "end")
        lines = int(self.text.index("end-1c").split(".")[0])
        for i in range(1, lines + 1):
            self.gutter.insert("end", f"{i}\n")
        self.gutter.config(state="disabled")
        self._sync_scroll()

    # ---------- edit ----------
    def _insert_tab(self, event):
        self.text.insert("insert", "    ")
        return "break"

    def _unindent(self, event):
        line = self.text.index("insert").split(".")[0]
        start = f"{line}.0"
        content = self.text.get(start, f"{line}.end")
        if content.startswith("    "):
            self.text.delete(start, f"{line}.4")
        elif content.startswith("\t"):
            self.text.delete(start, f"{line}.1")
        return "break"

    # ---------- API ----------
    def get_code(self):
        return self.text.get("1.0", "end-1c")

    def set_code(self, code):
        self.text.delete("1.0", "end")
        self.text.insert("1.0", code)
        self._refresh()

    def apply_theme(self):
        t = self.cfg.theme
        self.text.config(
            bg=t["bg"], fg=t["fg"],
            insertbackground=t["cursor"],
            selectbackground=t["select"],
            font=(self.cfg.get("editor_font"), self.cfg.get("editor_size")),
        )
        self.gutter.config(
            bg=t["gutter_bg"], fg=t["gutter_fg"],
            font=(self.cfg.get("editor_font"), self.cfg.get("editor_size")),
        )
        self.scroll.config(
            bg=t["bg"], troughcolor=t["gutter_bg"],
            activebackground=t["select"],
        )
        self._refresh()