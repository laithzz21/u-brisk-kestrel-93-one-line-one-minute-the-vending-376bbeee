#!/usr/bin/env python3
"""One line, one minute — the vending machine.

A vending machine flirts with a passer-by: one single line, at most 200
characters, full of machine vocabulary (coils, slots, buttons, exact
change) and charming rather than creepy.

The script prints the line to stdout (that print is the entry) and also
saves a copy under the output directory (``/output/entry.txt`` by default,
or ``$MAKEFUN_OUTPUT`` when set), reading the file back afterwards to
prove the copy matches.

Runs on Python 3.13 with the standard library only. Deterministic: no
network access, no clock reads, no randomness anywhere.
"""

import os
import sys

LINE = (
    "My coils spun the moment you walked by — and I don't even need "
    "exact change. Your favorite's been waiting in slot B4, so press "
    "me once: the first one's on the house."
)

MAX_LENGTH = 200
MACHINE_VOCAB = ("coil", "slot", "button", "change", "coin", "press")
OUTPUT_NAME = "entry.txt"


def check_length(line: str) -> int:
    """Return the character count, rejecting anything out of range."""
    count = len(line)
    if count < 1:
        raise ValueError("entry must not be empty")
    if count > MAX_LENGTH:
        raise ValueError(
            f"entry is {count} characters, over the {MAX_LENGTH} limit"
        )
    return count


def check_single_line(line: str) -> None:
    """The entry is one spoken line: no newlines, no blank text, no
    stray whitespace around the edges."""
    if "\n" in line or "\r" in line:
        raise ValueError("entry must be a single line")
    if not line.strip():
        raise ValueError("entry must not be blank")
    if line != line.strip():
        raise ValueError("entry must not have leading or trailing whitespace")


def check_machine_voice(line: str) -> None:
    """A flirt that could come from anyone is not the machine's line.
    At least one word from the machine's own vocabulary has to show up."""
    lowered = line.lower()
    hits = [word for word in MACHINE_VOCAB if word in lowered]
    if not hits:
        raise ValueError(
            "entry must sound like the machine (coils, slots, buttons, change)"
        )
    if len(hits) < 2:
        raise ValueError(
            "entry must use at least two machine words (coils, slots, buttons, change)"
        )


def check_line(line: str) -> None:
    """Run every validation on the entry before anything is printed."""
    check_length(line)
    check_single_line(line)
    check_machine_voice(line)


def pick_output_dir() -> str:
    """Choose where the copy goes: $MAKEFUN_OUTPUT first, then /output,
    and a local ./output directory if neither can be written to."""
    candidates = [os.environ.get("MAKEFUN_OUTPUT") or "/output"]
    for candidate in candidates:
        try:
            os.makedirs(candidate, exist_ok=True)
            probe = os.path.join(candidate, ".write_probe")
            with open(probe, "w", encoding="utf-8") as handle:
                handle.write("ok")
            os.remove(probe)
            return candidate
        except OSError:
            continue
    fallback = os.path.join(os.getcwd(), "output")
    os.makedirs(fallback, exist_ok=True)
    return fallback


def save_copy(line: str) -> str:
    """Write the line to entry.txt in the output directory, then read it
    back and confirm the stored copy is identical."""
    out_dir = pick_output_dir()
    path = os.path.join(out_dir, OUTPUT_NAME)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(line)
    with open(path, "r", encoding="utf-8") as handle:
        stored = handle.read()
    if stored != line:
        raise RuntimeError("read-back failed: stored entry does not match")
    if len(stored.encode("utf-8")) != len(line.encode("utf-8")):
        raise RuntimeError("read-back failed: stored entry byte length differs")
    return path


def run() -> int:
    check_line(LINE)
    # The stdout print is the entry itself, so it goes out first and
    # must succeed before any file work happens.
    print(LINE, flush=True)
    try:
        save_copy(LINE)
    except (OSError, RuntimeError) as exc:
        # The file copy is a convenience only; the printed entry is
        # already out, so a failed copy must not fail the run.
        print(f"warning: could not save {OUTPUT_NAME}: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
