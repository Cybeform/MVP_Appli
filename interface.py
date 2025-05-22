import os
import threading
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox

from backend.meeting_transcription import (
    start_recording,
    stop_recording,
    transcribe_audio,
    summarize_text,
    generate_word,
)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Enregistrement de Réunion")
        self.geometry("600x500")
        self.resizable(False, False)
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        self.frames = {}
        for Page in (HomePage, RecordPage, ReportPage):
            frame = Page(container, self)
            self.frames[Page.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.current_file = None
        self.transcription = None
        self.summary = None
        self.show_frame("HomePage")

    def show_frame(self, name: str):
        self.frames[name].tkraise()

class HomePage(tk.Frame):
    def __init__(self, parent, ctrl):
        super().__init__(parent)
        tk.Label(self, text="Bienvenue", font=("Helvetica", 20)).pack(pady=20)
        tk.Button(self, text="Démarrer enregistrement", width=25,
                  command=lambda: ctrl.show_frame("RecordPage")).pack(pady=5)
        tk.Button(self, text="Charger un fichier", width=25,
                  command=lambda: ctrl.show_frame("RecordPage")).pack(pady=5)

class RecordPage(tk.Frame):
    def __init__(self, parent, ctrl):
        super().__init__(parent)
        self.ctrl = ctrl
        self.is_recording = False

        tk.Label(self, text="Enregistrement / Upload", font=("Helvetica", 18)).pack(pady=10)

        self.btn_record = tk.Button(self, text="▶️ Démarrer", width=20, command=self.toggle_record)
        self.btn_record.pack(pady=5)

        tk.Button(self, text="📂 Choisir fichier", width=20, command=self._upload).pack(pady=5)

        self.status = tk.Label(self, text="", fg="green"); self.status.pack(pady=5)
        self.next_btn = tk.Button(self, text="Générer rapport", width=20, state="disabled",
                                  command=lambda: ctrl.show_frame("ReportPage"))
        self.next_btn.pack(pady=20)

    def toggle_record(self):
        if not self.is_recording:
            # démarrage
            self.is_recording = True
            self.btn_record.config(text="⏹️ Stop", fg="red")
            self.status.config(text="Enregistrement en cours…")
            threading.Thread(target=lambda: start_recording("meeting.wav"), daemon=True).start()
        else:
            # arrêt
            self.is_recording = False
            self.btn_record.config(text="▶️ Démarrer", fg="black")
            def _stop_and_ready():
                wav = stop_recording()
                self.ctrl.current_file = wav
                self.next_btn.config(state="normal")
                self.status.config(text=f"Fichier prêt : {wav}")
            threading.Thread(target=_stop_and_ready, daemon=True).start()

    def _upload(self):
        path = filedialog.askopenfilename(filetypes=[("Audio","*.wav *.mp3")])
        if path:
            self.ctrl.current_file = path
            self.next_btn.config(state="normal")
            self.status.config(text=f"Fichier sélectionné : {os.path.basename(path)}")

class ReportPage(tk.Frame):
    def __init__(self, parent, ctrl):
        super().__init__(parent)
        self.ctrl = ctrl

        tk.Label(self, text="Rapport de réunion", font=("Helvetica", 18)).pack(pady=10)
        self.txt_trans = scrolledtext.ScrolledText(self, height=10); self.txt_trans.pack(fill="both", expand=True, padx=10, pady=5)
        self.txt_sum   = scrolledtext.ScrolledText(self, height=5);  self.txt_sum.pack(fill="both", expand=True, padx=10, pady=5)

        btn_frame = tk.Frame(self); btn_frame.pack(fill="x", pady=10)
        self.btn_gen = tk.Button(btn_frame, text="Lancer génération", width=20, command=self._generate)
        self.btn_gen.pack(side="left", padx=5)
        tk.Button(btn_frame, text="Accueil", width=10, command=lambda: ctrl.show_frame("HomePage")).pack(side="left")
        self.btn_exp = tk.Button(btn_frame, text="Exporter Word", width=20, state="disabled", command=self._export)
        self.btn_exp.pack(side="right", padx=5)

    def _generate(self):
        audio = self.ctrl.current_file
        if not audio:
            messagebox.showwarning("Attention", "Aucun fichier audio")
            return
        self.btn_gen.config(state="disabled")
        self.txt_trans.delete("1.0", tk.END); self.txt_trans.insert(tk.END, "Transcription…")
        self.txt_sum.delete("1.0", tk.END)

        def task():
            text = transcribe_audio(audio)
            self.ctrl.transcription = text
            self.txt_trans.delete("1.0", tk.END); self.txt_trans.insert(tk.END, text)

            self.txt_sum.insert(tk.END, "Résumé…")
            summary = summarize_text(text)
            self.ctrl.summary = summary
            self.txt_sum.delete("1.0", tk.END); self.txt_sum.insert(tk.END, summary)

            self.btn_exp.config(state="normal")
        threading.Thread(target=task, daemon=True).start()

    def _export(self):
        doc = generate_word(self.ctrl.transcription, self.ctrl.summary)
        messagebox.showinfo("Succès", f"Document créé : {doc}")

if __name__ == "__main__":
    App().mainloop()
