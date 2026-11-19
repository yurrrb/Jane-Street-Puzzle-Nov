#!/usr/bin/env python3
"""Toolkit for Jane Street's November 2026 puzzle, "Pressure Points".

The puzzle gives no rules, only:
  * an empty-set symbol Ø,
  * 75 strings whose letters are sorted alphabetically (multisets, listed in order),
  * 19 emojis,
  * an answer enumeration "(11 12)".

Working hypothesis: every sorted string is the letters of a word or phrase.
Un-sorting them is step one; then you look for how they tie to the emojis.

Usage:
    python3 solve.py WORDLIST [--pairs] [--max-pair-len N]

WORDLIST is any file with one word or phrase per line (e.g. /usr/share/dict/words,
a Wikipedia title dump, or a crossword word list).
"""
import argparse
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).parent


def key(s: str) -> str:
    """Canonical anagram key: letters only, upper-case, sorted."""
    return "".join(sorted(re.sub(r"[^A-Z]", "", s.upper())))


def load_clues():
    lines = (HERE / "clues.txt").read_text(encoding="utf-8").splitlines()
    letters = [l for l in lines if re.fullmatch(r"[A-Z]+", l)]
    emojis = [l for l in lines if l not in letters and l not in ("Ø",) and not l.startswith("(")]
    return letters, emojis


def load_index(path):
    idx = defaultdict(set)
    for line in open(path, encoding="utf-8", errors="ignore"):
        w = line.strip()
        if w:
            idx[key(w)].add(w)
    return idx


def two_word_splits(target, idx, min_len=2):
    """All ways to write `target` (a sorted key) as word1 + word2."""
    tc = Counter(target)
    out = set()
    for k, words in idx.items():
        if min_len <= len(k) <= len(target) - min_len and not (Counter(k) - tc):
            rest = "".join(sorted((tc - Counter(k)).elements()))
            if rest in idx and k <= rest:
                for a in words:
                    for b in idx[rest]:
                        out.add(f"{a} + {b}")
    return sorted(out)


def stats(letters):
    total = Counter("".join(letters))
    print(f"{len(letters)} strings, {sum(total.values())} letters")
    print("letter totals:", " ".join(f"{c}{n}" for c, n in sorted(total.items())))
    print("letters never used:", "".join(c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if c not in total))
    print("length histogram:", dict(sorted(Counter(map(len, letters)).items())))
    unsorted = [l for l in letters if l != key(l)]
    print("strings not in sorted order (should be none):", unsorted)
    print("list itself sorted:", letters == sorted(letters))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("wordlist", nargs="?")
    ap.add_argument("--pairs", action="store_true", help="also try two-word splits for misses")
    args = ap.parse_args()

    letters, emojis = load_clues()
    stats(letters)
    print("emojis:", " ".join(emojis), f"({len(emojis)})")
    if not args.wordlist:
        print("\nPass a word list to un-anagram the strings.")
        return

    idx = load_index(args.wordlist)
    misses = []
    for s in letters:
        hits = sorted(idx.get(s, ()))
        if hits:
            print(f"{s:22} {', '.join(hits[:12])}")
        else:
            misses.append(s)
            print(f"{s:22} --")
    if args.pairs:
        print("\nTwo-word splits for misses:")
        for s in misses:
            splits = two_word_splits(s, idx)
            print(f"{s:22} {'; '.join(splits[:10]) or '--'}")


if __name__ == "__main__":
    sys.exit(main())
