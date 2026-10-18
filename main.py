import os
import tkinter as tk
from tkinter import ttk

import pygame
from pynput import keyboard

SOUND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")
EXTS = (".wav", ".ogg", ".mp3")

pygame.mixer.pre_init(44100, -16, 2, 256)
pygame.mixer.init()
pygame.mixer.set_num_channels(32)

class GunKeysApp:
    def __init__(self, root):
        self.root = root
        root.title("Gun Keys")
        root.geometry("320x190")
        root.resizable(False, False)

        self.sounds = self.load_sounds()
        self.current = None
        self.held = set()

        self.enabled = tk.BooleanVar(value=True)
        self.volume = tk.DoubleVar(value=0.8)

        frm = ttk.Frame(root, padding=15)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Gun sound").pack(anchor="w")
        self.combo = ttk.Combobox(
            frm, values=list(self.sounds.keys()), state="readonly"
        )
        self.combo.pack(fill="x", pady=(2, 12))
        self.combo.bind("<<ComboboxSelected>>", self.on_select)

        ttk.Label(frm, text="Volume").pack(anchor="w")
        ttk.Scale(
            frm, from_=0, to=1, variable=self.volume, command=self.on_volume
        ).pack(fill="x", pady=(2, 12))

        ttk.Checkbutton(frm, text="Enabled", variable=self.enabled).pack(anchor="w")

        self.status = ttk.Label(frm, text="Pick a gun")
        self.status.pack(anchor="w", pady=(8, 0))

        if self.sounds:
            self.combo.current(0)
            self.on_select()
        else:
            self.status.config(text="No sounds in /sounds folder")

        self.listener = keyboard.Listener(
            on_press=self.on_press, on_release=self.on_release
        )
        self.listener.start()
        root.protocol("WM_DELETE_WINDOW", self.close)

    def load_sounds(self):
        out = {}
        if not os.path.isdir(SOUND_DIR):
            os.makedirs(SOUND_DIR)
        for f in sorted(os.listdir(SOUND_DIR)):
            name, ext = os.path.splitext(f)
            if ext.lower() in EXTS:
                out[name] = pygame.mixer.Sound(os.path.join(SOUND_DIR, f))
        return out

    def on_select(self, event=None):
        name = self.combo.get()
        self.current = self.sounds[name]
        self.on_volume()
        self.current.play()  # preview
        self.status.config(text=f"Active: {name}")

    def on_volume(self, _=None):
        v = self.volume.get()
        for s in self.sounds.values():
            s.set_volume(v)

    def on_press(self, key):
        if key in self.held:  # ignore key repeat when held
            return
        self.held.add(key)
        if self.enabled.get() and self.current:
            self.current.play()

    def on_release(self, key):
        self.held.discard(key)

    def close(self):
        self.listener.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    GunKeysApp(root)
    root.mainloop()