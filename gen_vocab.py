#!/usr/bin/env python3
import re
from pathlib import Path

INPUT = Path("all_outputs.txt")
CPP_OUT = Path("vocab_VADER.cpp")
H_OUT   = Path("vocab_VADER.h")

HEADER_BANNER = (
    "// Talkie library\n"
    "// 2011 Peter Knight\n"
    "// Nerding and Hoarding 2025\n"
    "// This code is released under GPLv2 license.\n"
    "//\n"
)

INCLUDE_ARDUINO = '#include <Arduino.h>\n'

GUARD_TOP = (
    "#ifndef _TALKIE_VOCAB_VADER_H\n"
    "#define _TALKIE_VOCAB_VADER_H \n"
)

GUARD_BOTTOM = "#endif // _TALKIE_VOCAB_VOCAB_VADER_H\n"

def main():
    if not INPUT.exists():
        raise FileNotFoundError(f"Couldn't find {INPUT.resolve()}")

    raw = INPUT.read_text(encoding="utf-8", errors="ignore")

    # ---------- Build vocab_YOURvOICE.cpp ----------
    # Replace every "const unsigned char" with "extern const uint8_t"
    cpp_body = re.sub(r"\bconst\s+unsigned\s+char\b", "extern const uint8_t", raw)

    cpp_out = HEADER_BANNER + "\n" + INCLUDE_ARDUINO + "\n" + cpp_body
    CPP_OUT.write_text(cpp_out, encoding="utf-8")

    # ---------- Collect symbol names for the header ----------
    # Find array names declared as: const unsigned char NAME[] ...
    # (Use original text to be robust.)
    name_pattern = re.compile(
        r"\bconst\s+unsigned\s+char\s+([A-Za-z_][A-Za-z0-9_]*)\s*\[\]",
        flags=re.MULTILINE,
    )
    names = name_pattern.findall(raw)

    # De-duplicate but preserve order
    seen = set()
    ordered_names = []
    for n in names:
        if n not in seen:
            seen.add(n)
            ordered_names.append(n)

    # Prepare aligned declarations:
    # extern const uint8_t NAME[]     PROGMEM;
    if ordered_names:
        max_name_len = max(len(n) for n in ordered_names)
    else:
        max_name_len = 0

    decl_lines = []
    for n in ordered_names:
        # Align PROGMEM after the longest NAME[]
        padding = " " * (max_name_len - len(n) + 1)  # at least 1 space
        decl_lines.append(f"extern const uint8_t {n}[]{padding}PROGMEM;")

    header_out = (
        HEADER_BANNER
        + GUARD_TOP
        + "\n"
        + INCLUDE_ARDUINO
        + "\n"
        + "\n".join(decl_lines)
        + "\n\n"
        + GUARD_BOTTOM
    )
    H_OUT.write_text(header_out, encoding="utf-8")

    print(f"Wrote {CPP_OUT} and {H_OUT}")
    print(f"Total symbols declared: {len(ordered_names)}")

if __name__ == "__main__":
    main()
