#!/usr/bin/env python3
"""Measure pitch and delivery of voice lines (I can't listen, so this is how takes are compared).

Run from comment-build/:
    .venv/bin/python tools/voice_stats.py voice/ep03_el/*.wav

Per file: median pitch (Hz), pitch movement (standard deviation in semitones: under ~2 sounds flat,
3-5 lively, over ~6 theatrical), length, and average level (dB).
"""
import subprocess
import sys

import numpy as np

SR = 16000


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


def pitch_track(x, fmin=70.0, fmax=420.0):
    win, hop = int(0.04 * SR), int(0.01 * SR)
    lo, hi = int(SR / fmax), int(SR / fmin)
    f0 = []
    gate = 0.1 * (np.sqrt(np.mean(x ** 2)) + 1e-9)
    for i in range(0, len(x) - win, hop):
        fr = x[i:i + win] - np.mean(x[i:i + win])
        if np.sqrt(np.mean(fr ** 2)) < gate:
            continue
        ac = np.correlate(fr, fr, mode="full")[win - 1:]
        if ac[0] <= 0:
            continue
        ac = ac / ac[0]
        k = lo + int(np.argmax(ac[lo:hi]))
        if ac[k] > 0.5:
            f0.append(SR / k)
    return np.array(f0)


def stats(path):
    x = load(path)
    f0 = pitch_track(x)
    if len(f0) < 5:
        return None
    med = float(np.median(f0))
    f0 = f0[(f0 > med / 1.8) & (f0 < med * 1.8)]  # drop octave errors
    st = 12 * np.log2(f0 / np.median(f0))
    level = 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)
    return {"f0": float(np.median(f0)), "spread": float(np.std(st)), "dur": len(x) / SR, "level": float(level)}


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    print(f"{'file':28s} {'pitch Hz':>8s} {'movement st':>11s} {'len s':>6s} {'level dB':>8s}")
    for p in sys.argv[1:]:
        s = stats(p)
        name = p.split("/")[-1]
        if not s:
            print(f"{name:28s}  (no voiced frames)")
            continue
        print(f"{name:28s} {s['f0']:8.0f} {s['spread']:11.1f} {s['dur']:6.2f} {s['level']:8.1f}")


if __name__ == "__main__":
    main()
