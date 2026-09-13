# main.py(audit::v16)
import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import webbrowser

import customtkinter as ctk

from config import Config
from editor import LuaEditor
from repl import LuaREPL, detect_lua_bin
from tabs import TabBar

APP_NAME = "Lunar IDE"
APP_VERSION = "1.0.0"
LUNAR_DOCS = "https://www.lua.org/manual/5.4/"
LUNAR_REPO = "https://github.com/codebabel-appbag/lunar_idle/blob/main/lunaridle_project/source/docs/README.md"

GREEN_OK = "#2ea043"


class Lunar(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.cfg = Config()
        self.title(APP_NAME)
        self.geometry("640x480")
        self.resizable(False, False)
        self.update_idletasks()
        self._center_window(640, 480)

        self._tab_seq = 0
        self.tabs = {}
        self.repl_id = None
        self.config_tab_id = None
        self.m_file = None

        self._build_menu()
        self._build_ui()
        self.apply_theme()

        self.open_repl_tab()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ---------- centralizar ----------
    def _center_window(self, w, h):
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ---------- menu ----------
    def _build_menu(self):
        self.menubar = tk.Menu(self)

        self.m_file = tk.Menu(self.menubar, tearoff=0)
        self.m_file.add_command(label="New",     accelerator="Ctrl+N", command=self.new_file)
        self.m_file.add_command(label="Open",    accelerator="Ctrl+O", command=self.open_file)
        self.m_file.add_command(label="Save",    accelerator="Ctrl+S", command=self.save_file)
        self.m_file.add_command(label="Save As", accelerator="Ctrl+Shift+S", command=self.save_file_as)
        self.m_file.add_separator()
        self.m_file.add_command(label="Exit", command=self._on_close)
        self.menubar.add_cascade(label="File", menu=self.m_file)

        m_edit = tk.Menu(self.menubar, tearoff=0)
        m_edit.add_command(label="Undo",  accelerator="Ctrl+Z", command=lambda: self._edit("undo"))
        m_edit.add_command(label="Redo",  accelerator="Ctrl+Y", command=lambda: self._edit("redo"))
        m_edit.add_separator()
        m_edit.add_command(label="Cut",   accelerator="Ctrl+X", command=lambda: self._edit("cut"))
        m_edit.add_command(label="Copy",  accelerator="Ctrl+C", command=lambda: self._edit("copy"))
        m_edit.add_command(label="Paste", accelerator="Ctrl+V", command=lambda: self._edit("paste"))
        self.menubar.add_cascade(label="Edit", menu=m_edit)

        # Menu Run com F5
        m_run = tk.Menu(self.menubar, tearoff=0)
        m_run.add_command(label="Run App", accelerator="F5", command=self.run_app)
        self.menubar.add_cascade(label="Run", menu=m_run)

        m_opt = tk.Menu(self.menubar, tearoff=0)
        m_opt.add_command(label="Config", command=self.open_config)
        self.menubar.add_cascade(label="Option", menu=m_opt)

        m_help = tk.Menu(self.menubar, tearoff=0)
        m_help.add_command(label="About Lunar",      command=self.about)
        m_help.add_command(label="# About Tab Limit",  command=self.about_tab_limit)
        m_help.add_separator()
        m_help.add_command(label="Lunar Docs",       command=lambda: webbrowser.open(LUNAR_REPO))
        m_help.add_command(label="Lua Docs",         command=lambda: webbrowser.open(LUNAR_DOCS))
        self.menubar.add_cascade(label="Help", menu=m_help)

        self.config(menu=self.menubar)

        self.bind_all("<Control-n>", lambda e: self.new_file())
        self.bind_all("<Control-o>", lambda e: self.open_file())
        self.bind_all("<Control-s>", lambda e: self.save_file())
        self.bind_all("<Control-Shift-S>", lambda e: self.save_file_as())
        self.bind_all("<Control-w>", lambda e: self.close_current_tab())
        self.bind_all("<Control-z>", lambda e: self._edit("undo"))
        self.bind_all("<Control-y>", lambda e: self._edit("redo"))
        self.bind_all("<F5>", lambda e: self.run_app())

    def _update_menu_states(self):
        if not self.m_file:
            return
        
        limit_reached = self.tabbar.count_tabs() >= 6
        
        state = "disabled" if limit_reached else "normal"
        self.m_file.entryconfig("New", state=state)
        self.m_file.entryconfig("Open", state=state)
        
        if limit_reached:
            self.title(f"{APP_NAME} - [ Tabs limit: 6/6 ]")
        else:
            self.title(APP_NAME)

    def _check_tab_limit(self):
        return self.tabbar.count_tabs() >= 6

    # ---------- UI ----------
    def _build_ui(self):
        self.tabbar = TabBar(self, self.cfg,
                             on_select=self.select_tab,
                             on_close=self.close_tab)
        self.tabbar.pack(fill="x")

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

    # ---------- tema ----------
    def apply_theme(self):
        t = self.cfg.theme
        self.configure(fg_color=t["bg"])
        self.container.configure(fg_color=t["bg"])
        self.tabbar.apply_theme()

        for tab in self.tabs.values():
            w = tab["widget"]
            if hasattr(w, "apply_theme"):
                w.apply_theme()

        self._theme_menu(self.menubar, t)

    def _theme_menu(self, menu, t):
        try:
            menu.config(bg=t["menu_bg"], fg=t["fg"],
                        activebackground=t["select"],
                        activeforeground=t["fg"])
        except Exception:
            pass
        end = menu.index("end")
        if end is None:
            return
        for i in range(end + 1):
            try:
                if menu.type(i) == "cascade":
                    sub = menu.nametowidget(menu.entrycget(i, "menu"))
                    self._theme_menu(sub, t)
            except Exception:
                pass

    # ---------- tabs ----------
    def _new_tab_id(self):
        self._tab_seq += 1
        return f"tab{self._tab_seq}"

    def open_repl_tab(self):
        if self.repl_id and self.repl_id in self.tabs:
            self.select_tab(self.repl_id)
            return self.repl_id

        _path, versao = detect_lua_bin()
        titulo = f"REPL ~ : {versao}"

        tab_id = self._new_tab_id()
        widget = LuaREPL(self.container, self.cfg)
        self.tabs[tab_id] = {"kind": "repl", "widget": widget,
                             "path": None, "title": titulo}
        self.tabbar.add_tab(tab_id, titulo, closable=False)
        self.repl_id = tab_id
        self.select_tab(tab_id)
        self._update_menu_states()
        return tab_id

    def open_editor_tab(self, path=None, content=None, title=None):
        if self._check_tab_limit():
            return None

        tab_id = self._new_tab_id()
        widget = LuaEditor(self.container, self.cfg)
        if content is not None:
            widget.set_code(content)

        if title is None:
            title = "untitled" if path is None else os.path.basename(path)

        self.tabs[tab_id] = {"kind": "editor", "widget": widget,
                             "path": path, "title": title}
        self.tabbar.add_tab(tab_id, title)
        
        if path is not None:
            self.tabbar.set_tab_valid(tab_id, True)

        self.select_tab(tab_id)
        self._update_menu_states()
        return tab_id

    def open_config_tab(self):
        if self.config_tab_id and self.config_tab_id in self.tabs:
            self.select_tab(self.config_tab_id)
            return self.config_tab_id

        if self._check_tab_limit():
            return None

        tab_id = self._new_tab_id()
        widget = ConfigTab(self.container, self.cfg, self)
        self.tabs[tab_id] = {"kind": "config", "widget": widget,
                             "path": None, "title": "Configuration"}
        self.tabbar.add_tab(tab_id, "Configuration", closable=False)
        self.config_tab_id = tab_id
        self.select_tab(tab_id)
        self._update_menu_states()
        return tab_id

    def select_tab(self, tab_id):
        if tab_id not in self.tabs:
            return
        for tid, tab in self.tabs.items():
            tab["widget"].pack_forget()
        self.tabs[tab_id]["widget"].pack(fill="both", expand=True)
        self.tabbar.set_active(tab_id)
        w = self.tabs[tab_id]["widget"]
        if hasattr(w, "apply_theme"):
            w.apply_theme()

    def close_tab(self, tab_id, force=False):
        if tab_id not in self.tabs:
            return
        if tab_id == self.repl_id:
            return

        if tab_id == self.config_tab_id:
            w = self.tabs[tab_id]["widget"]
            if not force and hasattr(w, "request_close"):
                if not w.request_close():
                    return
            w.destroy()
            del self.tabs[tab_id]
            self.tabbar.remove_tab(tab_id)
            self.config_tab_id = None
            if self.tabs:
                self.select_tab(next(iter(self.tabs)))
            self._update_menu_states()
            return

        tab = self.tabs[tab_id]
        if tab["kind"] == "editor":
            code = tab["widget"].get_code()
            if code.strip():
                r = messagebox.askyesno("Close", f"Close '{tab['title']}'?")
                if not r:
                    return
        tab["widget"].destroy()
        del self.tabs[tab_id]
        self.tabbar.remove_tab(tab_id)
        if self.tabs:
            self.select_tab(next(iter(self.tabs)))
        self._update_menu_states()

    def close_current_tab(self):
        if not self.tabbar.active:
            return
        if self.tabbar.active == self.repl_id:
            return
        self.close_tab(self.tabbar.active)

    def _current(self):
        tid = self.tabbar.active
        return self.tabs.get(tid) if tid else None

    # ---------- file ----------
    def new_file(self):
        if self._check_tab_limit():
            return
        self.open_editor_tab()

    def open_file(self):
        if self._check_tab_limit():
            return
        path = filedialog.askopenfilename(
            filetypes=[("Lua", "*.lua"), ("all", "*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            messagebox.showerror("Erro", str(e))
            return
        self.open_editor_tab(path=path, content=content,
                             title=os.path.basename(path))

    def save_file(self):
        cur = self._current()
        if not cur or cur["kind"] != "editor":
            return
        if cur["path"] is None:
            return self.save_file_as()
        try:
            with open(cur["path"], "w", encoding="utf-8") as f:
                f.write(cur["widget"].get_code())
            cur["title"] = os.path.basename(cur["path"])
            self.tabbar.update_title(self.tabbar.active, cur["title"])
            self.tabbar.set_tab_valid(self.tabbar.active, True)
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def save_file_as(self):
        cur = self._current()
        if not cur or cur["kind"] != "editor":
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".lua",
            filetypes=[("Lua", "*.lua"), ("all", "*.*")])
        if not path:
            return
        cur["path"] = path
        self.save_file()

    # ---------- run app (F5) ----------
    def run_app(self):
        cur = self._current()
        if not cur or cur["kind"] != "editor":
            messagebox.showwarning("Run App", "Please select an active Lua editor tab to run.")
            return

        if cur["path"] is None:
            messagebox.showwarning(
                "Unsaved File",
                "This file is not saved yet!\n\nPlease save the file first (Ctrl+S) before running."
            )
            return

        filepath = cur["path"]
        lua_bin, _ = detect_lua_bin()
        if not lua_bin:
            messagebox.showerror("Error", "Lua interpreter not found in system path.")
            return

        try:
            result = subprocess.run(
                [lua_bin, filepath],
                capture_output=True,
                text=True,
                timeout=5
            )
            output = result.stdout
            error = result.stderr

            # Abre o REPL e injeta o resultado diretamente na janela dele
            self.open_repl_tab()
            repl_widget = self.tabs[self.repl_id]["widget"]

            if hasattr(repl_widget, "print_output"):
                run_text = f">>> running: {os.path.basename(filepath)}\n{output}"
                if error:
                    run_text += f"[stderr]:\n{error}"
                repl_widget.print_output(run_text.strip())

        except subprocess.TimeoutExpired:
            messagebox.showerror("Execution Error", "Script execution timed out (exceeded 5s).")
        except Exception as e:
            messagebox.showerror("Execution Error", str(e))

    # ---------- edit ----------
    def _edit(self, action):
        cur = self._current()
        if not cur:
            return
        w = cur["widget"]
        target = getattr(w, "text", None) or getattr(w, "console", None)
        if target is None:
            return
        try:
            if action == "undo":   target.event_generate("<<Undo>>")
            elif action == "redo": target.event_generate("<<Redo>>")
            elif action == "cut":  target.event_generate("<<Cut>>")
            elif action == "copy": target.event_generate("<<Copy>>")
            elif action == "paste":target.event_generate("<<Paste>>")
        except Exception:
            pass

    # ---------- config ----------
    def open_config(self):
        self.open_config_tab()

    # ---------- help ----------
    def about(self):
        messagebox.showinfo(
            "About Lunar",
            "Lunar IDLE\n\n"
            "A minimalist IDLE for Lua.\n"
            "Editor + REPL with tabs.\n\n"
            "Powered by minguantEcossys.\n"
            "codebabel for Lua devs.\n\n"
            f"lunar IDLE :: v"+APP_VERSION+".\n"
        )

    def about_tab_limit(self):
        messagebox.showinfo(
            "About Tab Limit",
            "Lunar IDLE is intentionally designed as a minimalist tool "
            "tailored for lightweight testing and quick script prototyping.\n\n"
            "To keep resource usage minimal and the workspace focused, "
            "the IDE enforces a maximum cap of 6 active tabs (REPL + 5 editors).\n\n"
            "When this threshold is reached, the 'New' and 'Open' file options "
            "are temporarily disabled until an active tab is closed."
        )

    # ---------- fechar ----------
    def _on_close(self):
        if self.repl_id and self.repl_id in self.tabs:
            w = self.tabs[self.repl_id]["widget"]
            if hasattr(w, "clear"):
                try:
                    w.clear()
                except Exception:
                    pass
            if hasattr(w, "shutdown"):
                try:
                    w.shutdown()
                except Exception:
                    pass
        self.destroy()


# ---------- tab de configuração ----------
class ConfigTab(ctk.CTkFrame):
    def __init__(self, master, cfg, app):
        super().__init__(master, fg_color="transparent")
        self.cfg = cfg
        self.app = app
        self._snapshot = self._read_snapshot()

        self._build_widgets()
        self.apply_theme()

    def _build_widgets(self):
        self.form = ctk.CTkFrame(self)
        self.form.pack(fill="both", expand=True, padx=20, pady=(20, 10))

        self.lbl_theme = ctk.CTkLabel(self.form, text="Theme",
                                      font=("Segoe UI", 12, "bold"))
        self.lbl_theme.grid(row=0, column=0, sticky="w", padx=(0, 20), pady=(0, 6))

        self.theme_var = tk.StringVar(value=self.cfg.get("theme"))
        theme_box = ctk.CTkFrame(self.form, fg_color="transparent")
        theme_box.grid(row=0, column=1, sticky="w", pady=(0, 6))
        self.rb_dark = ctk.CTkRadioButton(
            theme_box, text="Dark", variable=self.theme_var,
            value="dark", command=self._on_change)
        self.rb_light = ctk.CTkRadioButton(
            theme_box, text="Light", variable=self.theme_var,
            value="light", command=self._on_change)
        self.rb_dark.pack(side="left")
        self.rb_light.pack(side="left", padx=12)

        self.lbl_ed_font = ctk.CTkLabel(self.form, text="Font (editor)",
                                        font=("Segoe UI", 12, "bold"))
        self.lbl_ed_font.grid(row=1, column=0, sticky="w", padx=(0, 20), pady=(10, 6))
        self.ed_font = ctk.CTkEntry(self.form)
        self.ed_font.insert(0, self.cfg.get("editor_font"))
        self.ed_font.grid(row=1, column=1, sticky="ew", pady=(10, 6))
        self.ed_font.bind("<KeyRelease>", lambda e: self._on_change())

        self.lbl_ed_size = ctk.CTkLabel(self.form, text="Font Size (editor)",
                                        font=("Segoe UI", 12, "bold"))
        self.lbl_ed_size.grid(row=2, column=0, sticky="w", padx=(0, 20), pady=(10, 6))
        self.ed_size = ctk.CTkEntry(self.form)
        self.ed_size.insert(0, str(self.cfg.get("editor_size")))
        self.ed_size.grid(row=2, column=1, sticky="ew", pady=(10, 6))
        self.ed_size.bind("<KeyRelease>", lambda e: self._on_change())

        self.lbl_rp_font = ctk.CTkLabel(self.form, text="Font (REPL)",
                                        font=("Segoe UI", 12, "bold"))
        self.lbl_rp_font.grid(row=3, column=0, sticky="w", padx=(0, 20), pady=(10, 6))
        self.rp_font = ctk.CTkEntry(self.form)
        self.rp_font.insert(0, self.cfg.get("repl_font"))
        self.rp_font.grid(row=3, column=1, sticky="ew", pady=(10, 6))
        self.rp_font.bind("<KeyRelease>", lambda e: self._on_change())

        self.lbl_rp_size = ctk.CTkLabel(self.form, text="Font Size (REPL)",
                                        font=("Segoe UI", 12, "bold"))
        self.lbl_rp_size.grid(row=4, column=0, sticky="w", padx=(0, 20), pady=(10, 6))
        self.rp_size = ctk.CTkEntry(self.form)
        self.rp_size.insert(0, str(self.cfg.get("repl_size")))
        self.rp_size.grid(row=4, column=1, sticky="ew", pady=(10, 6))
        self.rp_size.bind("<KeyRelease>", lambda e: self._on_change())

        self.form.grid_columnconfigure(1, weight=1)

        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=20, pady=(10, 20))

        self.btn_save = ctk.CTkButton(bar, text="Save",
                                      command=self._on_save_click,
                                      width=100)
        self.btn_close = ctk.CTkButton(bar, text="Close",
                                       command=self._on_close_click,
                                       width=100)
        self.btn_save.pack(side="right")
        self.btn_close.pack(side="right", padx=(0, 8))

    def _read_snapshot(self):
        return (
            self.cfg.get("theme"),
            self.cfg.get("editor_font"),
            str(self.cfg.get("editor_size")),
            self.cfg.get("repl_font"),
            str(self.cfg.get("repl_size")),
        )

    def _current_fields(self):
        return (
            self.theme_var.get(),
            self.ed_font.get().strip(),
            self.ed_size.get().strip(),
            self.rp_font.get().strip(),
            self.rp_size.get().strip(),
        )

    def _is_dirty(self):
        return self._current_fields() != self._snapshot

    def _on_change(self):
        dirty = self._is_dirty()
        titulo = "*Configuration" if dirty else "Configuration"
        self.app.tabbar.update_title(self.app.config_tab_id, titulo)

        if dirty:
            self.btn_save.configure(fg_color=GREEN_OK, hover_color="#3fb950")
        else:
            self._reset_save_button_color()

    def _reset_save_button_color(self):
        default = ctk.ThemeManager.theme["CTkButton"]["fg_color"]
        hover = ctk.ThemeManager.theme["CTkButton"]["hover_color"]
        self.btn_save.configure(fg_color=default, hover_color=hover)

    def _on_save_click(self):
        try:
            new_theme = self.theme_var.get()
            new_ed_font = self.ed_font.get().strip() or "Consolas"
            new_ed_size = int(self.ed_size.get())
            new_rp_font = self.rp_font.get().strip() or "Consolas"
            new_rp_size = int(self.rp_size.get())
        except ValueError:
            messagebox.showerror("Erro", "Invalid font size.")
            return

        self.cfg.set("theme", new_theme)
        self.cfg.set("editor_font", new_ed_font)
        self.cfg.set("editor_size", new_ed_size)
        self.cfg.set("repl_font", new_rp_font)
        self.cfg.set("repl_size", new_rp_size)

        self.app.close_tab(self.app.config_tab_id, force=True)
        self.app.apply_theme()

    def _on_close_click(self):
        self.app.close_tab(self.app.config_tab_id)

    def request_close(self):
        if self._is_dirty():
            resp = messagebox.askokcancel(
                "Exit without saving?",
                "There are unsaved changes. Exit without saving?"
            )
            return bool(resp)
        return True

    def apply_theme(self):
        self.configure(fg_color="transparent")
        t = self.cfg.theme
        
        theme_mode = self.cfg.get("theme")
        ctk.set_appearance_mode("dark" if theme_mode == "dark" else "light")
        
        lbl_color = t["fg"]
        for lbl in [self.lbl_theme, self.lbl_ed_font, self.lbl_ed_size, self.lbl_rp_font, self.lbl_rp_size]:
            lbl.configure(text_color=lbl_color)
            
        self._on_change()


if __name__ == "__main__":
    app = Lunar()
    app.mainloop()