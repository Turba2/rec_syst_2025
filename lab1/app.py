from __future__ import annotations
import json
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

from config import load_config
from providers import TranslationRequest, DeepTranslateProvider, GoogleTranslateProvider

def quality_hint(text: str) -> str:
    if not text.strip():
        return "пусто"
    if len(text) < 5:
        return "коротко"
    return "ок"

class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("API Compare: Translation (Tkinter, lite)")
        self.geometry("980x640")

        cfg = load_config()
        self.prov_a = DeepTranslateProvider(cfg)
        self.prov_b = GoogleTranslateProvider(cfg)

        self._build_ui()

    def _build_ui(self) -> None:
        top = tk.Frame(self); top.pack(fill="x", padx=10, pady=8)
        tk.Label(top, text="From:").pack(side="left")
        self.lang_from = ttk.Combobox(top, values=["auto", "ru", "en", "de", "fr"], width=6)
        self.lang_from.set("ru"); self.lang_from.pack(side="left", padx=6)
        tk.Label(top, text="To:").pack(side="left")
        self.lang_to = ttk.Combobox(top, values=["ru", "en", "de", "fr"], width=6)
        self.lang_to.set("en"); self.lang_to.pack(side="left", padx=6)
        ttk.Button(top, text="Сравнить", command=self.on_compare).pack(side="right")

        center = tk.Frame(self); center.pack(fill="both", expand=True, padx=10, pady=4)

        left = tk.Frame(center); left.pack(side="left", fill="both", expand=True, padx=(0,6))
        tk.Label(left, text="Входной текст").pack(anchor="w")
        self.input_text = scrolledtext.ScrolledText(left, height=10)
        self.input_text.pack(fill="both", expand=True)

        right = tk.Frame(center); right.pack(side="left", fill="both", expand=True)

        pane_a = tk.LabelFrame(right, text="Провайдер A (DeepTranslate)")
        pane_a.pack(fill="both", expand=True, pady=(0,6))
        self.out_a = scrolledtext.ScrolledText(pane_a, height=6); self.out_a.pack(fill="both", expand=True)
        tk.Label(pane_a, text="JSON A").pack(anchor="w")
        self.json_a = scrolledtext.ScrolledText(pane_a, height=7); self.json_a.pack(fill="both", expand=True)

        pane_b = tk.LabelFrame(right, text="Провайдер B (GoogleTranslate)")
        pane_b.pack(fill="both", expand=True)
        self.out_b = scrolledtext.ScrolledText(pane_b, height=6); self.out_b.pack(fill="both", expand=True)
        tk.Label(pane_b, text="JSON B").pack(anchor="w")
        self.json_b = scrolledtext.ScrolledText(pane_b, height=7); self.json_b.pack(fill="both", expand=True)

        self.metrics_var = tk.StringVar(value="Метрики появятся здесь")
        tk.Label(self, textvariable=self.metrics_var).pack(anchor="w", padx=12, pady=(4,10))

    def on_compare(self) -> None:
        text = self.input_text.get("1.0", "end").strip()
        if not text:
            messagebox.showwarning("Нет текста", "Введите текст для перевода.")
            return
        req = TranslationRequest(self.lang_from.get(), self.lang_to.get(), text)

        a = self.prov_a.translate(req)
        b = self.prov_b.translate(req)

        self.out_a.delete("1.0", "end"); self.out_a.insert("1.0", a.translated_text or f"[пусто] (HTTP {a.status_code})")
        self.out_b.delete("1.0", "end"); self.out_b.insert("1.0", b.translated_text or f"[пусто] (HTTP {b.status_code})")

        self.json_a.delete("1.0", "end"); self.json_a.insert("1.0", json.dumps(a.raw_json, ensure_ascii=False, indent=2))
        self.json_b.delete("1.0", "end"); self.json_b.insert("1.0", json.dumps(b.raw_json, ensure_ascii=False, indent=2))

        self.metrics_var.set(
            f"len={len(text)} | A: {a.elapsed_ms} ms, {a.status_code}, {quality_hint(a.translated_text)} | "
            f"B: {b.elapsed_ms} ms, {b.status_code}, {quality_hint(b.translated_text)}"
        )

if __name__ == "__main__":
    App().mainloop()
