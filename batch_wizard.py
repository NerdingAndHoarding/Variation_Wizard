import subprocess
import pathlib

# === CONFIGURATION ===
INPUT_FOLDER = pathlib.Path(".")              # Folder with WAV files
OUTPUT_FILE = "all_outputs.txt"               # Output text file
PYTHON_WIZARD = pathlib.Path(__file__).parent / "python_wizard.py"

# === ALL python_wizard OPTIONS (from README) ===
# Set to True/False for flags, or provide a value as string/number
wizard_options = {
    "-u": None,             # unvoicedThreshold (float/int)
    "-w": 1,             # windowWidth (int)
    "-U": False,            # normalizeUnvoicedRMS (flag)
    "-V": True,            # normalizeVoicedRMS (flag)
    "-S": True,             # includeExplicitStopFrame (flag)
    "-p": True,             # preEmphasis (flag)
    "-a": None,             # preEmphasisAlpha (float)
    "-d": False,            # debug (flag)
    "-r": "50,200",        # pitchRange (comma-separated string)
    "-F": None,             # frameRate (int)
    "-m": None,             # subMultipleThreshold (int/float)
    "-f": "arduino",        # outputFormat {arduino,C,hex,python}
    "-T": "tms5220",        # tablesVariant {tms5220,tms5100}
}

# === SCRIPT ===
def build_command(wav_file: pathlib.Path):
    cmd = ["python", str(PYTHON_WIZARD)]
    for opt, val in wizard_options.items():
        if val is None:
            continue                  # skip unset
        if isinstance(val, bool):
            if val:                   # only include if True
                cmd.append(opt)
        else:
            cmd.extend([opt, str(val)])
    cmd.append(str(wav_file))         # add wav file at the end
    return cmd

def main():
    wav_files = sorted(INPUT_FOLDER.glob("*.wav"))
    if not wav_files:
        print("No WAV files found in", INPUT_FOLDER)
        return

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for wav in wav_files:
            print(f"Processing {wav.name} ...")
            cmd = build_command(wav)
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                out.write(f"//--- {wav.name} //---\n")
                out.write(result.stdout)
                out.write("\n\n")
            except subprocess.CalledProcessError as e:
                print(f"Error processing {wav}: {e.stderr}")

    print(f"Done. All outputs written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
