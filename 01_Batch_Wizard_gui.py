import subprocess
import pathlib
import tkinter as tk
from tkinter import filedialog, messagebox

# === DEFAULT CONFIG ===
PYTHON_WIZARD = pathlib.Path(__file__).parent / "python_wizard.py"

wizard_options = {
    "-u": 20,
    "-w": 1,
    "-U": False,
    "-V": True,
    "-S": True,
    "-p": True,
    "-a": None,
    "-d": False,
    "-r": "50,500",
    "-F": None,
    "-m": None,
    "-f": "arduino",
    "-T": "tms5220",
}

# === BUILD COMMAND ===
def build_command(wav_file):
    cmd = ["python", str(PYTHON_WIZARD)]
    for opt, val in wizard_options.items():
        if val is None:
            continue
        if isinstance(val, bool):
            if val:
                cmd.append(opt)
        else:
            cmd.extend([opt, str(val)])
    cmd.append(str(wav_file))
    return cmd


# === GUI APP ===
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Batch_Wizard. Python_Wizard. (step 1)")

        self.input_folder = tk.StringVar(value=".")
        self.output_file = tk.StringVar(value="all_outputs.txt")
	
	 # --- info selection ---

        tk.Label(root, text="    Create an LPC voice for Talkie Arduino Library.             ").grid(row=0, column=1, sticky="w") 
        tk.Label(root, text="Select WAV folder (mono, 8 kHz, 16-bit), to generate a temp TXT,").grid(row=1, column=1, sticky="w") 
        tk.Label(root, text="then open it in gen_vocab_gui_new to build your ARDUINO voice.  ").grid(row=2, column=1, sticky="w") 
	 
        # --- Folder selection ---

        tk.Label(root, text="Input Folder:").grid(row=3, column=0, sticky="w")
        tk.Entry(root, textvariable=self.input_folder, width=40).grid(row=3, column=1)
        tk.Button(root, text="Browse", command=self.browse_folder).grid(row=3, column=2)

        # --- Output file ---
        tk.Label(root, text="Output File:").grid(row=4, column=0, sticky="w")
        tk.Entry(root, textvariable=self.output_file, width=40).grid(row=4, column=1)
        tk.Button(root, text="Save As", command=self.save_file).grid(row=4, column=2)

        # --- Options ---
        self.option_vars = {}
        row = 5
        tk.Label(root, text="Options:").grid(row=row, column=0, sticky="w")
        row += 1

        for opt, val in wizard_options.items():
            if isinstance(val, bool):
                var = tk.BooleanVar(value=val)
                tk.Checkbutton(root, text=opt, variable=var).grid(row=row, column=0, sticky="w")
            else:
                var = tk.StringVar(value="" if val is None else str(val))
                tk.Label(root, text=opt).grid(row=row, column=0, sticky="e")
                tk.Entry(root, textvariable=var, width=20).grid(row=row, column=1, sticky="w")

            self.option_vars[opt] = var
            row += 1

        # --- Run button ---
        tk.Button(root, text="Run", command=self.run).grid(row=row, column=0, columnspan=3, pady=10)

        # --- Log output ---
        self.log = tk.Text(root, height=15, width=70)
        self.log.grid(row=row+1, column=0, columnspan=3)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.input_folder.set(folder)

    def save_file(self):
        file = filedialog.asksaveasfilename(defaultextension=".txt")
        if file:
            self.output_file.set(file)

    def log_print(self, text):
        self.log.insert(tk.END, text + "\n")
        self.log.see(tk.END)
        self.root.update()

    def update_options(self):
        for opt, var in self.option_vars.items():
            val = var.get()
            if isinstance(wizard_options[opt], bool):
                wizard_options[opt] = var.get()
            else:
                wizard_options[opt] = val if val != "" else None

    def run(self):
        self.update_options()

        input_path = pathlib.Path(self.input_folder.get())
        output_path = self.output_file.get()

        wav_files = sorted(input_path.glob("*.wav"))
        if not wav_files:
            messagebox.showwarning("No files", "No WAV files found.")
            return

        with open(output_path, "w", encoding="utf-8") as out:
            for wav in wav_files:
                self.log_print(f"Processing {wav.name}...")
                cmd = build_command(wav)

                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    out.write(f"//--- {wav.name} //---\n")
                    out.write(result.stdout + "\n\n")

                except subprocess.CalledProcessError as e:
                    self.log_print(f"Error: {wav.name}")
                    self.log_print(e.stderr)

        self.log_print(f"\nDone! Output saved to {output_path}")


# === MAIN ===
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()