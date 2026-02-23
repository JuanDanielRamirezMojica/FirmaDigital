"""
app_firma.py - Interfaz Gráfica para Firma Digital
===================================================
Front-end visual para GenSig.py y VerSig.py.
Toda la lógica criptográfica vive en esos dos archivos.

Uso:
    python app_firma.py

Requiere que GenSig.py y VerSig.py estén en la misma carpeta.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

# ── Importar lógica desde los módulos CLI ──────────────────────────────────────
from GenSig import generate_keys, sign_file, save_public_key, save_private_key, load_private_key, save_signature
from VerSig import verify_file

# ─────────────────────────────────────────────
# COLORES
# ─────────────────────────────────────────────
BG      = "#0f1117"
PANEL   = "#1a1d27"
BORDER  = "#2a2d3e"
ACCENT  = "#6c63ff"
ACCENT2 = "#00d9a6"
TEXT    = "#e8e8f0"
SUBTEXT = "#6b6d82"
SUCCESS = "#00d9a6"
ERROR   = "#ff5c7a"
WARNING = "#f5a623"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Firma Digital RSA")
        self.geometry("700x750")
        self.resizable(False, False)
        self.configure(bg=BG)

        self.doc_path     = tk.StringVar(value="")
        self.privkey_path = tk.StringVar(value="")
        self.pubkey_ver   = tk.StringVar(value="")
        self.sig_ver      = tk.StringVar(value="")
        self.doc_ver      = tk.StringVar(value="")

        self._build_ui()

    # ── UI ──────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        hdr = tk.Frame(self, bg=BG, pady=24)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🔐 Firma Digital RSA", font=("Courier New", 22, "bold"),
                 bg=BG, fg=ACCENT).pack()
        tk.Label(hdr, text="SHA-256  ·  2048 bits  ·  PSS padding",
                 font=("Courier New", 10), bg=BG, fg=SUBTEXT).pack(pady=(2, 0))

        tab_bar = tk.Frame(self, bg=BG)
        tab_bar.pack(fill="x", padx=30)
        self.tab_content = tk.Frame(self, bg=BG)
        self.tab_content.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        self.btn_tab_sign = self._tab_btn(tab_bar, "FIRMAR",    lambda: self._show_tab("sign"))
        self.btn_tab_sign.pack(side="left", padx=(0, 4))
        self.btn_tab_ver  = self._tab_btn(tab_bar, "VERIFICAR", lambda: self._show_tab("verify"))
        self.btn_tab_ver.pack(side="left")

        self._build_sign_tab()
        self._build_verify_tab()
        self._show_tab("sign")

    def _tab_btn(self, parent, text, cmd):
        return tk.Button(parent, text=text, command=cmd,
                         font=("Courier New", 10, "bold"),
                         bg=PANEL, fg=SUBTEXT, relief="flat",
                         padx=20, pady=10, cursor="hand2",
                         activebackground=ACCENT, activeforeground="white")

    def _show_tab(self, tab):
        if tab == "sign":
            self.frame_sign.pack(fill="both", expand=True)
            self.frame_verify.pack_forget()
            self.btn_tab_sign.config(bg=ACCENT, fg="white")
            self.btn_tab_ver.config(bg=PANEL, fg=SUBTEXT)
        else:
            self.frame_verify.pack(fill="both", expand=True)
            self.frame_sign.pack_forget()
            self.btn_tab_ver.config(bg=ACCENT, fg="white")
            self.btn_tab_sign.config(bg=PANEL, fg=SUBTEXT)

    # ── TAB FIRMAR ──────────────────────────────────────────────────────────────

    def _build_sign_tab(self):
        self.frame_sign = tk.Frame(self.tab_content, bg=BG)

        tk.Label(self.frame_sign, text="DOCUMENTO A FIRMAR",
                 font=("Courier New", 9, "bold"), bg=BG, fg=SUBTEXT).pack(anchor="w", pady=(20, 4))
        self._drop_zone(self.frame_sign, "Clic para seleccionar el archivo a firmar",
                        self._pick_doc).pack(fill="x")
        tk.Label(self.frame_sign, textvariable=self.doc_path,
                 font=("Courier New", 9), bg=BG, fg=ACCENT2, wraplength=600).pack(anchor="w", pady=(4, 0))

        tk.Label(self.frame_sign, text="LLAVE PRIVADA (opcional)",
                 font=("Courier New", 9, "bold"), bg=BG, fg=SUBTEXT).pack(anchor="w", pady=(16, 4))
        row = tk.Frame(self.frame_sign, bg=BG)
        row.pack(fill="x")
        self._btn(row, "📂 Cargar private_key.pem", self._pick_privkey).pack(side="left")
        self._btn(row, "✨ Generar nueva", self._clear_privkey, color=BORDER).pack(side="left", padx=(8, 0))
        tk.Label(self.frame_sign, textvariable=self.privkey_path,
                 font=("Courier New", 9), bg=BG, fg=WARNING, wraplength=600).pack(anchor="w", pady=(4, 0))

        tk.Frame(self.frame_sign, bg=BORDER, height=1).pack(fill="x", pady=20)
        self._btn(self.frame_sign, " FIRMAR DOCUMENTO", self._do_sign,
                  color=ACCENT, big=True).pack(fill="x")

        self.log_sign = self._log_box(self.frame_sign)

    def _pick_doc(self, event=None):
        path = filedialog.askopenfilename(title="Selecciona el documento a firmar")
        if path:
            self.doc_path.set(path)
            self._log(self.log_sign, f"📄 Documento seleccionado: {os.path.basename(path)}", ACCENT2)

    def _pick_privkey(self):
        path = filedialog.askopenfilename(title="Selecciona tu llave privada",
                                          filetypes=[("PEM", "*.pem"), ("Todos", "*.*")])
        if path:
            self.privkey_path.set(path)
            self._log(self.log_sign, f"🔑 Llave privada seleccionada: {os.path.basename(path)}", WARNING)

    def _clear_privkey(self):
        self.privkey_path.set("")
        self._log(self.log_sign, "✨ Se generará una llave privada nueva al firmar.", SUBTEXT)

    def _do_sign(self):
        doc = self.doc_path.get()
        if not doc:
            messagebox.showwarning("Falta archivo", "Primero selecciona un documento.")
            return

        self._log(self.log_sign, "─" * 40, BORDER)
        self._log(self.log_sign, "Iniciando proceso de firma...", TEXT)

        privkey_file = self.privkey_path.get()

        if privkey_file:
            # ── Cargar llave privada existente (lógica de GenSig.load_private_key) ──
            pwd = simpledialog.askstring("Contraseña", "Contraseña de la llave privada:", show="*")
            if pwd is None:
                return
            try:
                private_key = load_private_key(privkey_file, password=pwd)
                self._log(self.log_sign, "✔ Llave privada cargada.", SUCCESS)
            except Exception as e:
                self._log(self.log_sign, f"✘ Error al cargar llave: {e}", ERROR)
                return
        else:
            # ── Generar nuevo par de llaves (lógica de GenSig.generate_keys) ──
            private_key, _ = generate_keys()
            self._log(self.log_sign, "✔ Par de llaves RSA 2048-bit generado.", SUCCESS)

            guardar = messagebox.askyesno("Guardar llave privada",
                                          "¿Deseas guardar la llave privada para reutilizarla?\n"
                                          "(recomendado si firmarás más documentos con la misma identidad)")
            if guardar:
                pwd = simpledialog.askstring("Contraseña", "Crea una contraseña para protegerla:", show="*")
                if pwd:
                    dest = filedialog.asksaveasfilename(defaultextension=".pem",
                                                        initialfile="private_key.pem",
                                                        filetypes=[("PEM", "*.pem")])
                    if dest:
                        save_private_key(private_key, filename=dest, password=pwd)
                        self._log(self.log_sign, f"✔ Llave privada guardada: {os.path.basename(dest)}", SUCCESS)

        # ── Guardar llave pública (lógica de GenSig.save_public_key) ──
        public_key = private_key.public_key()
        folder     = os.path.dirname(doc)
        pub_path   = os.path.join(folder, "public_key.pem")
        save_public_key(public_key, pub_path)
        self._log(self.log_sign, "✔ Llave pública guardada: public_key.pem", SUCCESS)

        # ── Firmar archivo (lógica de GenSig.sign_file + save_signature) ──
        try:
            signature = sign_file(private_key, doc)
            sig_path  = os.path.join(folder, "signature.bin")
            save_signature(signature, sig_path)
            self._log(self.log_sign, f"✔ Firma generada: signature.bin ({len(signature)} bytes)", SUCCESS)
            self._log(self.log_sign, "─" * 40, BORDER)
            self._log(self.log_sign, "DOCUMENTO FIRMADO EXITOSAMENTE", SUCCESS)
            self._log(self.log_sign, f"   Archivos guardados en:\n   {folder}", SUBTEXT)
        except Exception as e:
            self._log(self.log_sign, f"✘ Error al firmar: {e}", ERROR)

    # ── TAB VERIFICAR ────────────────────────────────────────────────────────────

    def _build_verify_tab(self):
        self.frame_verify = tk.Frame(self.tab_content, bg=BG)

        for label, var, pick in [
            ("LLAVE PÚBLICA (.pem)",  self.pubkey_ver, self._pick_pubkey),
            ("FIRMA (.bin)",          self.sig_ver,    self._pick_sig),
            ("DOCUMENTO ORIGINAL",    self.doc_ver,    self._pick_doc_ver),
        ]:
            tk.Label(self.frame_verify, text=label,
                     font=("Courier New", 9, "bold"), bg=BG, fg=SUBTEXT).pack(anchor="w", pady=(16, 4))
            self._drop_zone(self.frame_verify, "Clic para seleccionar", pick).pack(fill="x")
            tk.Label(self.frame_verify, textvariable=var,
                     font=("Courier New", 9), bg=BG, fg=ACCENT2, wraplength=600).pack(anchor="w", pady=(4, 0))

        tk.Frame(self.frame_verify, bg=BORDER, height=1).pack(fill="x", pady=20)
        self._btn(self.frame_verify, "🔍  VERIFICAR FIRMA", self._do_verify,
                  color=ACCENT2, big=True).pack(fill="x")

        self.log_verify = self._log_box(self.frame_verify)

    def _pick_pubkey(self, e=None):
        p = filedialog.askopenfilename(filetypes=[("PEM", "*.pem"), ("Todos", "*.*")])
        if p:
            self.pubkey_ver.set(p)
            self._log(self.log_verify, f" Llave pública: {os.path.basename(p)}", ACCENT2)

    def _pick_sig(self, e=None):
        p = filedialog.askopenfilename(filetypes=[("BIN", "*.bin"), ("Todos", "*.*")])
        if p:
            self.sig_ver.set(p)
            self._log(self.log_verify, f"Firma: {os.path.basename(p)}", ACCENT2)

    def _pick_doc_ver(self, e=None):
        p = filedialog.askopenfilename()
        if p:
            self.doc_ver.set(p)
            self._log(self.log_verify, f"Documento: {os.path.basename(p)}", ACCENT2)

    def _do_verify(self):
        pub = self.pubkey_ver.get()
        sig = self.sig_ver.get()
        doc = self.doc_ver.get()

        if not all([pub, sig, doc]):
            messagebox.showwarning("Faltan archivos", "Selecciona los 3 archivos: llave pública, firma y documento.")
            return

        self._log(self.log_verify, "─" * 40, BORDER)
        self._log(self.log_verify, "Verificando firma digital...", TEXT)

        try:
            # ── Verificar (lógica de VerSig.verify_file) ──
            result = verify_file(pub, sig, doc)
            self._log(self.log_verify, "─" * 40, BORDER)
            if result:
                self._log(self.log_verify, " signature verifies: TRUE", SUCCESS)
                self._log(self.log_verify, "   El documento es auténtico e íntegro.", SUBTEXT)
            else:
                self._log(self.log_verify, " signature verifies: FALSE", ERROR)
                self._log(self.log_verify, "   El documento fue alterado o la firma no corresponde.", SUBTEXT)
        except Exception as e:
            self._log(self.log_verify, f"✘ Error: {e}", ERROR)

    # ── COMPONENTES REUTILIZABLES ────────────────────────────────────────────────

    def _drop_zone(self, parent, text, cmd):
        frame = tk.Frame(parent, bg=PANEL, relief="flat", bd=0,
                         highlightthickness=1, highlightbackground=BORDER, cursor="hand2")
        lbl = tk.Label(frame, text=text, font=("Courier New", 10), bg=PANEL, fg=SUBTEXT, pady=18)
        lbl.pack(expand=True)
        frame.bind("<Button-1>", cmd)
        lbl.bind("<Button-1>", cmd)
        frame.bind("<Enter>", lambda e: frame.config(highlightbackground=ACCENT))
        frame.bind("<Leave>", lambda e: frame.config(highlightbackground=BORDER))
        return frame

    def _btn(self, parent, text, cmd, color=PANEL, big=False):
        return tk.Button(parent, text=text, command=cmd,
                         font=("Courier New", 12 if big else 10, "bold"),
                         bg=color, fg="white", relief="flat",
                         padx=16, pady=14 if big else 8, cursor="hand2",
                         activebackground=ACCENT, activeforeground="white")

    def _log_box(self, parent):
        frame = tk.Frame(parent, bg=PANEL, highlightthickness=1, highlightbackground=BORDER)
        frame.pack(fill="both", expand=True, pady=(12, 0))
        txt = tk.Text(frame, bg=PANEL, fg=TEXT, font=("Courier New", 9),
                      relief="flat", padx=12, pady=10, height=7,
                      state="disabled", wrap="word")
        txt.pack(fill="both", expand=True)
        for tag, color in [("success", SUCCESS), ("error", ERROR), ("warning", WARNING),
                            ("accent", ACCENT2), ("dim", SUBTEXT), ("border", BORDER), ("normal", TEXT)]:
            txt.tag_config(tag, foreground=color)
        return txt

    def _log(self, widget, msg, color=TEXT):
        tag_map = {SUCCESS: "success", ERROR: "error", WARNING: "warning",
                   ACCENT2: "accent", SUBTEXT: "dim", BORDER: "border", TEXT: "normal"}
        widget.config(state="normal")
        widget.insert("end", msg + "\n", tag_map.get(color, "normal"))
        widget.see("end")
        widget.config(state="disabled")


if __name__ == "__main__":
    App().mainloop()