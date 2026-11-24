#!/usr/bin/env python3
"""Entry for make.fun bounty: one line, one minute — the vending machine.

A single pickup line as if a vending machine were flirting with a passing
human, at most 200 characters. It must sound like the machine (slots,
buttons, coils, exact change) and be charming, not creepy.

Prints the single-line pickup line to stdout and also writes it to the
output directory (``/output/entry.txt`` by default, or ``$MAKEFUN_OUTPUT``
when set), verifying the written file by reading it back.

Python 3.13, stdlib only, deterministic: no network, clock, or randomness.
"""

import os
import sys

ENTRY = (
    "My coils spun the moment you walked by — and I don't even need "
    "exact change. Your favorite's been waiting in slot B4, so press "
    "me once: the first one's on the house."
)


MACHINE_WORDS = ("coil", "slot", "button", "change", "coin", "press")


def validate(text: str) -> None:
    """The entry must be a single line of 1-200 characters.

    A line the machine speaks must not be blank and must not carry
    stray leading or trailing whitespace. It must also sound like the
    machine: at least one word from its own vocabulary (coils, slots,
    buttons, exact change) has to appear, or the flirt could come from
    anyone.
    """
    if not 1 <= len(text) <= 200:
        raise ValueError(f"entry must be 1-200 characters, got {len(text)}")
    if "\n" in text or "\r" in text:
        raise ValueError("entry must be a single line")
    if not text.strip():
        raise ValueError("entry must not be blank")
    if text != text.strip():
        raise ValueError("entry must not have leading or trailing whitespace")
    lowered = text.lower()
    if not any(word in lowered for word in MACHINE_WORDS):
        raise ValueError("entry must sound like the machine (coils, slots, buttons, change)")


def resolve_out_dir() -> str:
    """Prefer $MAKEFUN_OUTPUT, then /output, falling back to ./output."""
    requested = os.environ.get("MAKEFUN_OUTPUT") or "/output"
    try:
        os.makedirs(requested, exist_ok=True)
        probe = os.path.join(requested, ".write_probe")
        with open(probe, "w", encoding="utf-8") as f:
            f.write("ok")
        os.remove(probe)
        return requested
    except OSError:
        fallback = os.path.join(os.getcwd(), "output")
        os.makedirs(fallback, exist_ok=True)
        return fallback


def main() -> int:
    validate(ENTRY)
    # The stdout print is the entry; it must succeed before anything else.
    print(ENTRY, flush=True)
    try:
        out_dir = resolve_out_dir()
        path = os.path.join(out_dir, "entry.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(ENTRY)
        # Verify the written file by reading it back.
        with open(path, "r", encoding="utf-8") as f:
            written = f.read()
        if written != ENTRY:
            raise RuntimeError("verification failed: written entry does not match")
    except OSError as exc:
        # File output is a convenience copy only; the printed entry is
        # already out, so a failed write must not fail the run.
        print(f"warning: could not write entry.txt: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
