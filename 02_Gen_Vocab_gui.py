#!/usr/bin/env python3
import re
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

HEADER_BANNER = (
    "// Talkie library\n"
    "// 2011 Peter Knight\n"
    "// Nerding and Hoarding 2026\n"
    "// GPLv2 License\n\n"
)

INCLUDE_ARDUINO = "#include <Arduino.h>\n\n"


# =========================================================
# SAFE PROGMEM BLOCK EXTRACTOR (DO NOT BREAK DATA)
# =========================================================
def extract_arrays(txt):
    """
    Extract full blocks like:

    const unsigned char _001[] PROGMEM = { ... };
    """

    pattern = re.compile(
        r"(const\s+unsigned\s+char\s+[A-Za-z0-9_]+\[\]\s+PROGMEM\s*=\s*\{[\s\S]*?\};)",
        re.MULTILINE
    )

    blocks = pattern.findall(txt)

    results = []

    for block in blocks:
        name_match = re.search(r"char\s+([A-Za-z0-9_]+)\[\]", block)
        if not name_match:
            continue

        name = name_match.group(1)

        data_match = re.search(r"\{([\s\S]*?)\};", block)
        if not data_match:
            continue

        data = data_match.group(1).strip()

        results.append((name, data))

    return results


# =========================================================
# INO GENERATOR
# =========================================================
def generate_ino(name, symbols, out_dir):
    count = len(symbols)

    letters = ",\n  ".join(symbols)
    names = ", ".join(f"\"{s}\"" for s in symbols)

    ino = f"""#include "Talkie.h"
#include "vocab_{name}.h"

Talkie voice(true, false);

const uint8_t* LETTERS[{count}] = {{
  {letters}
}};

const char* LETTER_NAMES[{count}] = {{
  {names}
}};

void setup() {{
  Serial.begin(115200);
  voice.doNotUseInvertedOutput(true);

  Serial.println(F("Talkie ready"));
  Serial.print(F("Samples: "));
  Serial.println({count});
}}

void loop() {{
  if (Serial.available()) {{
    int i = Serial.parseInt();

    if (i >= 1 && i <= {count}) {{
      Serial.println(LETTER_NAMES[i - 1]);
      voice.say(LETTERS[i - 1]);
    }}

    while (Serial.available()) Serial.read();
  }}
}}
"""

    path = out_dir / f"talkie_{name}.ino"
    path.write_text(ino, encoding="utf-8")
    return path


# =========================================================
# GUI APP
# =========================================================
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Generate_vocab. Python_wizard. Step 2")

        self.name = tk.StringVar()
        self.txt = tk.StringVar()
        self.wav = tk.StringVar()

        tk.Label(root, text="Project Name:").grid(row=0, column=0)
        tk.Entry(root, textvariable=self.name, width=30).grid(row=0, column=1)

        tk.Label(root, text="TXT file:").grid(row=1, column=0)
        tk.Entry(root, textvariable=self.txt, width=30).grid(row=1, column=1)
        tk.Button(root, text="Browse", command=self.pick_txt).grid(row=1, column=2)

        tk.Label(root, text="WAV folder:").grid(row=2, column=0)
        tk.Entry(root, textvariable=self.wav, width=30).grid(row=2, column=1)
        tk.Button(root, text="Browse", command=self.pick_wav).grid(row=2, column=2)

        tk.Button(root, text="GENERATE", command=self.generate).grid(row=3, column=0, columnspan=3)

        self.log = tk.Text(root, height=15, width=90)
        self.log.grid(row=4, column=0, columnspan=3)

    # ---------------- UI ----------------
    def pick_txt(self):
        f = filedialog.askopenfilename(filetypes=[("Text", "*.txt")])
        if f:
            self.txt.set(f)

    def pick_wav(self):
        f = filedialog.askdirectory()
        if f:
            self.wav.set(f)

    def log_print(self, msg):
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)
        self.root.update()

    # ---------------- MAIN ----------------
    def generate(self):
        name = self.name.get().strip().upper()
        txt_path = Path(self.txt.get())
        wav_path = Path(self.wav.get())

        if not name:
            messagebox.showerror("Error", "Enter project name")
            return

        if not txt_path.exists():
            messagebox.showerror("Error", "TXT file not found")
            return

        if not wav_path.exists():
            messagebox.showerror("Error", "WAV folder not found")
            return

        raw = txt_path.read_text(encoding="utf-8", errors="ignore")
        wav_files = sorted(wav_path.glob("*.wav"))

        arrays = extract_arrays(raw)

        self.log_print(f"TXT SIZE: {len(raw)}")
        self.log_print(f"ARRAYS FOUND: {len(arrays)}")
        self.log_print(f"WAV FILES: {len(wav_files)}")

        if not arrays:
            messagebox.showerror("Error", "No PROGMEM arrays found.")
            return

        if not wav_files:
            messagebox.showerror("Error", "No WAV files found")
            return

        arrays = arrays[:len(wav_files)]

        # =====================================================
        # OUTPUT FOLDER = SAME NAME AS INO
        # =====================================================
        out_dir = Path(f"talkie_{name}")
        out_dir.mkdir(exist_ok=True)

        symbols = [f"z_{i:03d}" for i in range(1, len(arrays) + 1)]

        # =====================================================
        # waveData.txt
        # =====================================================
        with open(out_dir / "waveData.txt", "w", encoding="utf-8") as f:
            for i, ((old, _), wav) in enumerate(zip(arrays, wav_files), start=1):
                f.write(f"z_{i:03d} = {wav.name} ({old})\n")

        # =====================================================
        # HEADER FILE
        # =====================================================
        h = HEADER_BANNER
        h += f"#ifndef VOCAB_{name}_H\n#define VOCAB_{name}_H\n\n"
        h += INCLUDE_ARDUINO

        for s in symbols:
            h += f"extern const uint8_t {s}[] PROGMEM;\n"

        h += "\n#endif\n"

        (out_dir / f"vocab_{name}.h").write_text(h, encoding="utf-8")

        # =====================================================
        # CPP FILE (FIXED: extern const)
        # =====================================================
        cpp = HEADER_BANNER + INCLUDE_ARDUINO

        for i, (old_name, data) in enumerate(arrays, start=1):
            sym = f"z_{i:03d}"
            cpp += f"extern const uint8_t {sym}[] PROGMEM = {{{data}}};\n\n"

        (out_dir / f"vocab_{name}.cpp").write_text(cpp, encoding="utf-8")

        # =====================================================
        # INO FILE
        # =====================================================
        ino = generate_ino(name, symbols, out_dir)

        self.log_print("=== SUCCESS ===")
        self.log_print(f"Output: {out_dir}")
        self.log_print(f"Samples: {len(symbols)}")
        self.log_print(f"INO: {ino.name}")


# =========================================================
# RUN
# =========================================================
if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()