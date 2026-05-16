import subprocess
import pathlib
import tkinter as tk
from tkinter import filedialog, messagebox
import itertools
import re

# === CONFIG ===
PYTHON_WIZARD = pathlib.Path(__file__).parent / "python_wizard.py"

PARAMS = {
    "-u": (10, 40, 3),
    "-w": (1, 3, 3),
    "-r_min": (20, 100, 3),
    "-r_max": (200, 800, 3),
}

INT_PARAMS = ["-u", "-w", "-r_min", "-r_max"]

FIXED_OPTIONS = {
    "-U": False,
    "-V": True,
    "-S": True,
    "-p": True,
    "-a": None,
    "-d": False,
    "-F": None,
    "-m": None,
    "-f": "arduino",
    "-T": "tms5220",
}


# === HELPERS ===
def linspace(start, end, steps, as_int=False):
    if steps <= 1:
        return [int(start) if as_int else start]

    step = (end - start) / (steps - 1)
    values = [start + i * step for i in range(steps)]

    if as_int:
        return [int(round(v)) for v in values]
    else:
        return [round(v, 4) for v in values]


def build_command(wav_file, combo):
    cmd = ["python", str(PYTHON_WIZARD)]

    # fixed options
    for opt, val in FIXED_OPTIONS.items():
        if val is None:
            continue
        if isinstance(val, bool):
            if val:
                cmd.append(opt)
        else:
            cmd.extend([opt, str(val)])

    r_min = combo.get("-r_min")
    r_max = combo.get("-r_max")

    for opt, val in combo.items():
        if opt in ["-r_min", "-r_max"]:
            continue

        if opt in INT_PARAMS:
            cmd.extend([opt, str(int(val))])
        else:
            cmd.extend([opt, str(val)])

    if r_min is not None and r_max is not None:
        cmd.extend(["-r", f"{int(r_min)},{int(r_max)}"])

    cmd.append(str(wav_file))
    return cmd


def build_param_string(combo):
    parts = []

    for opt, val in combo.items():
        if opt in ["-r_min", "-r_max"]:
            continue

        if opt in INT_PARAMS:
            parts.append(f"{opt} {int(val)}")
        else:
            parts.append(f"{opt} {val}")

    # add combined -r
    if "-r_min" in combo and "-r_max" in combo:
        parts.append(f"-r {int(combo['-r_min'])},{int(combo['-r_max'])}")

    # add fixed options
    for opt, val in FIXED_OPTIONS.items():
        if val is None:
            continue
        if isinstance(val, bool):
            if val:
                parts.append(opt)
        else:
            parts.append(f"{opt} {val}")

    return " ".join(parts)


# === GUI ===
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Variation_Wizard")

        self.input_file = tk.StringVar(value="")
        self.output_file = tk.StringVar(value="variations_output.txt")

        tk.Label(root, text="Generate parameter variations for python_wizard").grid(row=0, column=0, columnspan=3)

        # Input WAV
        tk.Label(root, text="Input WAV File:").grid(row=1, column=0)
        tk.Entry(root, textvariable=self.input_file, width=40).grid(row=1, column=1)
        tk.Button(root, text="Browse", command=self.browse_file).grid(row=1, column=2)

        # Output file
        tk.Label(root, text="Output File:").grid(row=2, column=0)
        tk.Entry(root, textvariable=self.output_file, width=40).grid(row=2, column=1)
        tk.Button(root, text="Save As", command=self.save_file).grid(row=2, column=2)

        # Table headers
        tk.Label(root, text="Param").grid(row=3, column=0)
        tk.Label(root, text="Min").grid(row=3, column=1)
        tk.Label(root, text="Max").grid(row=3, column=2)
        tk.Label(root, text="Steps").grid(row=3, column=3)

        self.entries = {}

        row = 4
        for p, (mn, mx, st) in PARAMS.items():
            tk.Label(root, text=p).grid(row=row, column=0)

            vmin = tk.DoubleVar(value=mn)
            vmax = tk.DoubleVar(value=mx)
            vsteps = tk.IntVar(value=st)

            tk.Entry(root, textvariable=vmin, width=8).grid(row=row, column=1)
            tk.Entry(root, textvariable=vmax, width=8).grid(row=row, column=2)
            tk.Entry(root, textvariable=vsteps, width=8).grid(row=row, column=3)

            self.entries[p] = (vmin, vmax, vsteps)
            row += 1

        tk.Button(root, text="Run Variations", command=self.run).grid(row=row, column=0, columnspan=4)

        self.log = tk.Text(root, height=15, width=70)
        self.log.grid(row=row+1, column=0, columnspan=4)

    def browse_file(self):
        file = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if file:
            self.input_file.set(file)

    def save_file(self):
        file = filedialog.asksaveasfilename(defaultextension=".txt")
        if file:
            self.output_file.set(file)

    def log_print(self, text):
        self.log.insert(tk.END, text + "\n")
        self.log.see(tk.END)
        self.root.update()

    def run(self):
        try:
            wav_path = pathlib.Path(self.input_file.get())
            if not wav_path.exists():
                messagebox.showerror("Error", "Invalid WAV file.")
                return

            base_name = wav_path.stem

            # build ranges
            param_values = {}
            for p, (vmin, vmax, vsteps) in self.entries.items():
                is_int = p in INT_PARAMS
                param_values[p] = linspace(vmin.get(), vmax.get(), vsteps.get(), is_int)

            keys = list(param_values.keys())
            combos = list(itertools.product(*(param_values[k] for k in keys)))

            self.log_print(f"Total combinations: {len(combos)}")

            # main output
            with open(self.output_file.get(), "w", encoding="utf-8") as out, \
                 open("variation_data.txt", "w", encoding="utf-8") as meta:

                idx = 1

                for combo_vals in combos:
                    combo = dict(zip(keys, combo_vals))

                    if combo["-r_min"] > combo["-r_max"]:
                        continue

                    name = f"{base_name}_{idx:03d}"

                    self.log_print(f"{name} | {combo}")

                    cmd = build_command(wav_path, combo)

                    try:
                        result = subprocess.run(
                            cmd,
                            capture_output=True,
                            text=True,
                            check=True
                        )

                        # rename array
                        modified = re.sub(
                            r'const unsigned char \w+\[\]',
                            f'const unsigned char {name}[]',
                            result.stdout
                        )

                        # write main output
                        out.write(f"//--- {name}.wav //---\n")
                        out.write(modified.strip() + "\n")

                        # write parameter log
                        param_str = build_param_string(combo)
                        meta.write(f"{name}: {param_str}\n")

                        idx += 1

                    except subprocess.CalledProcessError as e:
                        self.log_print("Error:")
                        self.log_print(e.stderr)

            self.log_print("Done!")

        except Exception as e:
            messagebox.showerror("Error", str(e))


# === MAIN ===
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()