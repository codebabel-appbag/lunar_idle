# config.py
import json, os

CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".lunar_config.json")

DEFAULTS = {
    "theme": "dark",
    "editor_font": "Consolas",
    "editor_size": 13,
    "repl_font": "Consolas",
    "repl_size": 13,
}

THEMES = {
    "dark": {
        "bg":        "#1e1e1e",
        "fg":        "#d4d4d4",
        "gutter_bg": "#252526",
        "gutter_fg": "#858585",
        "cursor":    "#aeafad",
        "select":    "#264f78",
        "tab_bg":    "#2d2d2d",
        "tab_active":"#1e1e1e",
        "tab_fg":    "#cccccc",
        "menu_bg":   "#2d2d2d",
        # highlight
        "kw":   "#569cd6",
        "str":  "#ce9178",
        "com":  "#6a9955",
        "num":  "#b5cea8",
        "fn":   "#dcdcaa",
        "op":   "#d4d4d4",
        "repl_in":  "#4ec9b0",
        "repl_out": "#d4d4d4",
        "repl_err": "#f48771",
    },
    "light": {
        "bg":        "#ffffff",
        "fg":        "#1e1e1e",
        "gutter_bg": "#f3f3f3",
        "gutter_fg": "#999999",
        "cursor":    "#000000",
        "select":    "#add6ff",
        "tab_bg":    "#ececec",
        "tab_active":"#ffffff",
        "tab_fg":    "#333333",
        "menu_bg":   "#f3f3f3",
        "kw":   "#0000ff",
        "str":  "#a31515",
        "com":  "#008000",
        "num":  "#098658",
        "fn":   "#795e26",
        "op":   "#1e1e1e",
        "repl_in":  "#267f99",
        "repl_out": "#1e1e1e",
        "repl_err": "#cd3131",
    },
}

class Config:
    def __init__(self):
        self.data = dict(DEFAULTS)
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH) as f:
                    self.data.update(json.load(f))
            except Exception:
                pass

    def save(self):
        try:
            with open(CONFIG_PATH, "w") as f:
                json.dump(self.data, f, indent=2)
        except Exception:
            pass

    def get(self, k, default=None):
        return self.data.get(k, default)

    def set(self, k, v):
        self.data[k] = v
        self.save()

    @property
    def theme(self):
        return THEMES[self.data["theme"]]