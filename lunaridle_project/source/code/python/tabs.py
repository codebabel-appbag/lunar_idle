# tabs.py(v4)
import tkinter as tk


class TabBar(tk.Frame):
    def __init__(self, master, cfg, on_select, on_close):
        super().__init__(master)
        self.cfg = cfg
        self.on_select = on_select
        self.on_close = on_close
        self.tabs = []
        self.active = None
        self.configure(bg=cfg.theme["tab_bg"])

    def count_tabs(self):
        return len(self.tabs)

    def add_tab(self, tab_id, title, closable=True):
        t = self.cfg.theme
        container = tk.Frame(self, bg=t["tab_bg"])
        container.pack(side="left", padx=(0, 1))

        btn = tk.Label(container, text=title, padx=10, pady=4,
                       bg=t["tab_bg"], fg=t["tab_fg"],
                       font=("Segoe UI", 10))
        btn.pack(side="left")
        btn.bind("<Button-1>", lambda e, i=tab_id: self.on_select(i))

        close = None
        if closable:
            close = tk.Label(container, text="✕", padx=6,
                             bg=t["tab_bg"], fg=t["tab_fg"],
                             font=("Segoe UI", 9))
            close.pack(side="left")
            close.bind("<Button-1>", lambda e, i=tab_id: self.on_close(i))

        self.tabs.append({"id": tab_id, "container": container,
                          "btn": btn, "close": close, "closable": closable, "is_valid": False})
        self.set_active(tab_id)

    def remove_tab(self, tab_id):
        for i, tb in enumerate(self.tabs):
            if tb["id"] == tab_id:
                tb["container"].destroy()
                self.tabs.pop(i)
                break
        if self.active == tab_id:
            self.active = None
            if self.tabs:
                self.set_active(self.tabs[0]["id"])

    def set_active(self, tab_id):
        t = self.cfg.theme
        self.active = tab_id
        for tb in self.tabs:
            is_active = (tb["id"] == tab_id)
            bg = t["tab_active"] if is_active else t["tab_bg"]
            
            # Gerenciamento de cor e negrito: Aba ativa validada ganha verde e bold
            if is_active and tb.get("is_valid", False):
                fg = "#2ea043"
                font = ("Segoe UI", 10, "bold")
            else:
                fg = t["fg"] if is_active else t["tab_fg"]
                font = ("Segoe UI", 10)

            tb["container"].config(bg=bg)
            tb["btn"].config(bg=bg, fg=fg, font=font)
            if tb["close"]:
                tb["close"].config(bg=bg, fg=fg)

    def set_tab_valid(self, tab_id, is_valid):
        for tb in self.tabs:
            if tb["id"] == tab_id:
                tb["is_valid"] = is_valid
                # Atualiza visual imediatamente se for a aba ativa
                if tb["id"] == self.active:
                    self.set_active(tab_id)
                break

    def update_title(self, tab_id, title):
        for tb in self.tabs:
            if tb["id"] == tab_id:
                tb["btn"].config(text=title)
                break

    def is_closable(self, tab_id):
        for tb in self.tabs:
            if tb["id"] == tab_id:
                return tb["closable"]
        return True

    def apply_theme(self):
        t = self.cfg.theme
        self.configure(bg=t["tab_bg"])
        for tb in self.tabs:
            is_active = (tb["id"] == self.active)
            bg = t["tab_active"] if is_active else t["tab_bg"]
            
            if is_active and tb.get("is_valid", False):
                fg = "#2ea043"
                font = ("Segoe UI", 10, "bold")
            else:
                fg = t["fg"] if is_active else t["tab_fg"]
                font = ("Segoe UI", 10)

            tb["container"].config(bg=bg)
            tb["btn"].config(bg=bg, fg=fg, font=font)
            if tb["close"]:
                tb["close"].config(bg=bg, fg=fg)