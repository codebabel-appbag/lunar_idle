# repl.py(v16)
import tkinter as tk
import subprocess
import threading
import shutil
import pty
import os
import re

# ---------- púrpura do prompt (hardcoded — config.py intocado) ----------
PROMPT_COLOR = {
    "dark":  "#c586c0",   # púrpura claro
    "light": "#7c3aed",   # púrpura escuro
}

MAX_CHARS = 100_000  # gatilho de limpeza automática

# Regex para limpar códigos de escape ANSI (como o bracketed paste \x1b[?2004h)
ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')


def detect_lua_bin():
    """Procura um binário lua no PATH. Retorna (path, versao) ou (None, 'unknown')."""
    for name in ("lua", "lua5.4", "lua5.3", "lua5.2", "lua5.1", "luajit"):
        path = shutil.which(name)
        if not path:
            continue
        try:
            out = subprocess.run([path, "-v"], capture_output=True,
                                 text=True, timeout=2)
            text = (out.stdout or "") + (out.stderr or "")
            versao = "unknown"
            for token in text.split():
                if token[0].isdigit():
                    versao = "Lua " + token
                    break
            return path, versao
        except Exception:
            return path, "unknown"
    return None, "unknown"


class LuaREPL(tk.Frame):
    def __init__(self, master, cfg):
        super().__init__(master)
        self.cfg = cfg
        t = cfg.theme

        self._char_count = 0
        self._proc = None
        self._reader_threads = []
        self._master_fd = None
        self._last_sent_code = ""

        # ---------- widget ----------
        self.console = tk.Text(
            self, wrap="word",
            bg=t["bg"], fg=t["repl_out"],
            insertbackground=t["cursor"],
            selectbackground=t["select"],
            relief="flat", borderwidth=0,
            font=(cfg.get("repl_font"), cfg.get("repl_size")),
            padx=8, pady=6,
        )
        
        # ---------- scrollbar visível ----------
        self.scroll = tk.Scrollbar(
            self, orient="vertical", command=self.console.yview,
        )
        self.console.configure(yscrollcommand=self.scroll.set)

        self.scroll.pack(side="right", fill="y")
        self.console.pack(side="left", fill="both", expand=True)

        self._config_tags()
        
        # ---------- Eventos de proteção e controle (Estilo IDLE) ----------
        self.console.bind("<Return>", self._on_enter)
        self.console.bind("<BackSpace>", self._on_backspace)
        self.console.bind("<Key>", self._on_key_press)
        self.console.bind("<Button-1>", self._on_click)

        # ---------- processo lua ----------
        self._start_lua()

        # prompt inicial
        self._write_prompt()

    # ---------------- lua subprocess (com PTY limpo) ----------------
    def _start_lua(self):
        path, _versao = detect_lua_bin()
        if not path:
            self._proc = None
            self._write_static("Lua não disponível.\n", "err")
            return
        try:
            master_fd, slave_fd = pty.openpty()
            self._proc = subprocess.Popen(
                [path],
                stdin=slave_fd,
                stdout=slave_fd,
                stderr=slave_fd,
                text=True,
                bufsize=0,
            )
            self._master_fd = master_fd
            os.close(slave_fd)
        except Exception as e:
            self._proc = None
            self._write_static("Lua não disponível.\n", "err")
            return

        t_out = threading.Thread(target=self._read_pty_stream,
                                 daemon=True)
        t_out.start()
        self._reader_threads = [t_out]

    def _read_pty_stream(self):
        """Lê do pseudo-terminal e joga no console via after() (thread-safe)."""
        try:
            while self._proc and self._proc.poll() is None:
                data = os.read(self._master_fd, 1024).decode('utf-8', errors='ignore')
                if not data:
                    break
                self.after(0, self._append_output, data, "out")
        except Exception:
            pass

    def _append_output(self, s, tag):
        """Insere o retorno do Lua filtrando o eco duplicado e o prompt nativo."""
        s_clean = ANSI_ESCAPE.sub('', s)
        s_clean = s_clean.replace("> ", "").replace("\r", "")
        
        # Se o PTY ecoou exatamente o código que acabamos de enviar, removemos do output
        if self._last_sent_code and self._last_sent_code in s_clean:
            s_clean = s_clean.replace(self._last_sent_code, "")
            self._last_sent_code = ""

        if not s_clean.strip():
            return

        if "input_start" in self.console.mark_names():
            insert_pos = self.console.index("input_start linestart")
            self.console.insert(insert_pos, s_clean, tag)
        else:
            self.console.insert("end", s_clean, tag)
            
        self.console.see("end")
        self._char_count += len(s_clean)
        if self._char_count >= MAX_CHARS:
            self._auto_clean()

    # ---------------- tags ----------------
    def _config_tags(self):
        t = self.cfg.theme
        theme_name = self.cfg.get("theme")
        self.console.tag_config(
            "in",
            foreground=PROMPT_COLOR.get(theme_name, PROMPT_COLOR["dark"]),
            font=(self.cfg.get("repl_font"), self.cfg.get("repl_size"), "bold"),
        )
        self.console.tag_config("out", foreground=t["repl_out"])
        self.console.tag_config("err", foreground=t["repl_err"])
        self.console.tag_config("sys", foreground=t["gutter_fg"])

    # ---------------- escrita estática ----------------
    def _write_static(self, s, tag="out"):
        s_clean = ANSI_ESCAPE.sub('', s)
        if "input_start" in self.console.mark_names():
            pos = self.console.index("input_start linestart")
            self.console.insert(pos, s_clean, tag)
        else:
            self.console.insert("end", s_clean, tag)
        self.console.see("end")
        self._char_count += len(s_clean)

    def _write_prompt(self):
        self.console.insert("end", "lua:: ", "in")
        self.console.mark_set("input_start", "end-1c")
        self.console.mark_gravity("input_start", "left")
        self.console.see("end")
        self.console.focus_set()

    # ---------------- Método público para injetar output externo (F5) ----------------
    def print_output(self, text):
        """Escreve o resultado do F5 de forma isolada e limpa antes do prompt atual."""
        clean_text = text.strip()
        if not clean_text:
            return

        formatted = f"\n{clean_text}\n"
        if "input_start" in self.console.mark_names():
            pos = self.console.index("input_start linestart")
            self.console.insert(pos, formatted, "out")
        else:
            self.console.insert("end", formatted, "out")
            
        self.console.see("end")
        self._char_count += len(formatted)

    # ---------------- Restrições estilo IDLE (Isolamento de edição) ----------------
    def _on_backspace(self, event):
        if self.console.compare("insert", "<=", "input_start"):
            return "break"

    def _on_key_press(self, event):
        if event.char and self.console.compare("insert", "<", "input_start"):
            self.console.mark_set("insert", "end")

    def _on_click(self, event):
        clicked_index = self.console.index(f"@{event.x},{event.y}")
        if self.console.compare(clicked_index, "<", "input_start"):
            self.console.mark_set("insert", "end")
            return "break"

    # ---------------- limpeza ----------------
    def _auto_clean(self):
        self.console.delete("1.0", "end")
        self._char_count = 0
        self._write_static("[REPL limpo — limite atingido]\n", "sys")
        self._write_prompt()

    def clear(self):
        """Chamado pelo main ao fechar a aplicação."""
        self.console.delete("1.0", "end")
        self._char_count = 0
        self._write_prompt()

    # ---------------- execução ----------------
    def _on_enter(self, event):
        code = self.console.get("input_start", "end-1c")
        self._last_sent_code = code.strip()

        self.console.insert("end", "\n")
        self.console.mark_set("input_start", "end")

        if self._proc and self._proc.poll() is None:
            try:
                os.write(self._master_fd, (code + "\n").encode('utf-8'))
            except Exception:
                self._write_static("Lua não disponível.\n", "err")
        else:
            if code.strip():
                self._write_static("Lua não disponível.\n", "err")

        self._write_prompt()
        return "break"

    # ---------------- tema ----------------
    def apply_theme(self):
        t = self.cfg.theme
        self.console.config(
            bg=t["bg"], fg=t["repl_out"],
            insertbackground=t["cursor"],
            selectbackground=t["select"],
            font=(self.cfg.get("repl_font"), self.cfg.get("repl_size")),
        )
        self._config_tags()

    # ---------------- fechar ----------------
    def shutdown(self):
        """Mata o processo lua com elegância e fecha o PTY."""
        if self._master_fd is not None:
            try:
                os.close(self._master_fd)
            except Exception:
                pass
            self._master_fd = None

        if self._proc and self._proc.poll() is None:
            try:
                self._proc.terminate()
                self._proc.wait(timeout=1)
            except Exception:
                try:
                    self._proc.kill()
                except Exception:
                    pass
        self._proc = None