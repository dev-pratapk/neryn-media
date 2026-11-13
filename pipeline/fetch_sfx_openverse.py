#!/usr/bin/env python3
"""Fetch CC0 / public-domain sound effects from Openverse for the Neryn episode template.

Run from comment-build/:
    python3 tools/fetch_sfx_openverse.py shorts/ep02-v4/assets/sfx-openverse [REF_DIR]
    python3 tools/fetch_sfx_openverse.py OUT REF_DIR --levels-only     # only re-level files already converted

For each of the 15 effect names the template uses, it searches the Openverse audio API (anonymous: 20
requests a minute, 200 a day), keeps only CC0 / public-domain results that are short enough, downloads the
best candidates into <out>/raw/ (untrusted files; they are only ever read by ffmpeg), converts the winner to
<out>/<name>.mp3 (mono, trimmed, peak-normalised, padded to the length the template expects) and writes
<out>/CREDITS.md. Nothing is executed from the downloads.
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request

API = "https://api.openverse.org/v1/audio/"
UA = "neryn-sfx-fetch/1.0"
# name: (search queries, min s, max s, length s the template expects)
SPEC = {
    "click":            (["click", "button click"], 0.03, 0.6, 0.37),
    "click-soft":       (["soft click", "light click"], 0.04, 0.7, 0.37),
    "key-press":        (["keyboard key press", "key press"], 0.04, 0.7, 0.40),
    "pop":              (["pop", "bubble pop"], 0.06, 1.0, 0.72),
    "typing":           (["typing keyboard", "keyboard typing"], 1.2, 4.0, 1.60),
    "whoosh":           (["whoosh", "swoosh"], 0.3, 1.5, 0.57),
    "whoosh-short":     (["short whoosh", "swish"], 0.15, 0.9, 0.57),
    "whoosh-cinematic": (["cinematic whoosh", "whoosh riser"], 1.0, 3.5, 2.00),
    "impact-bass-1":    (["bass impact", "deep boom"], 1.0, 3.5, 2.00),
    "impact-bass-2":    (["cinematic impact", "impact hit"], 1.5, 4.0, 2.40),
    "notification":     (["notification", "notification ding"], 0.4, 2.2, 1.50),
    "chime":            (["chime", "success chime"], 0.8, 3.5, 2.00),
    "sparkle":          (["sparkle", "magic sparkle"], 0.5, 2.5, 1.20),
    "pen_short":        (["pen scribble", "pencil writing"], 0.3, 1.6, 0.75),
    "stamp_real2":      (["rubber stamp", "stamp"], 0.15, 1.0, 0.55),
}
# a result must mention one of these words in its title or tags, and none of the "bad" ones
MUST = {
    "click": {"click"}, "click-soft": {"click"}, "key-press": {"key", "keyboard", "keypress"}, "pop": {"pop"},
    "typing": {"typing", "keyboard", "typewriter"}, "whoosh": {"whoosh", "swoosh", "swish"}, "whoosh-short": {"whoosh", "swoosh", "swish"},
    "whoosh-cinematic": {"whoosh", "swoosh", "riser", "cinematic"}, "impact-bass-1": {"impact", "boom", "bass"},
    "impact-bass-2": {"impact", "hit", "boom"}, "notification": {"notification", "ding", "alert"}, "chime": {"chime", "bell"},
    "sparkle": {"sparkle", "magic", "twinkle", "glitter", "shimmer"}, "pen_short": {"pen", "pencil", "scribble", "writing"}, "stamp_real2": {"stamp"},
}
BAD = {"impact-bass-2": {"door", "wood"}, "whoosh-cinematic": {"fire", "flame"}, "click": {"mouse"}, "pop": {"balloon", "cracker", "confetti"}}
LEAD_SILENCE = {"typing": 0.42}  # the template starts typing clips 0.42 s in, so the file keeps that much silence first


def get(url, timeout=40):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=timeout)


def search(q):
    params = {"q": q, "license": "cc0,pdm", "page_size": 20}
    with get(API + "?" + urllib.parse.urlencode(params)) as r:
        return json.load(r).get("results", [])


def probe(path):
    """(duration s, mean dB, peak dB) of an audio file, or None if ffmpeg cannot read it."""
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", path, "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True)
    dur = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr)
    mean = re.search(r"mean_volume: (-?[\d.]+) dB", r.stderr)
    peak = re.search(r"max_volume: (-?[\d.]+) dB", r.stderr)
    if not (dur and mean and peak):
        return None
    h, m, s = dur.groups()
    return int(h) * 3600 + int(m) * 60 + float(s), float(mean.group(1)), float(peak.group(1))


def convert(src, dst, want_len, lead):
    trim = "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.01"
    chain = f"{trim},areverse,{trim},areverse"
    parts = [chain, "alimiter=limit=0.9"]
    if lead:
        parts.append(f"adelay={int(lead * 1000)}")
    parts.append(f"apad=whole_dur={want_len}")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-t", str(want_len), "-ac", "1", "-ar", "44100",
                    "-af", ",".join(parts) + f",atrim=0:{want_len},volume=-1dB", "-codec:a", "libmp3lame", "-b:a", "128k", dst], check=True)


def mean_db(path):
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", path, "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True)
    m = re.search(r"mean_volume: (-?[\d.]+) dB", r.stderr)
    return float(m.group(1)) if m else None


def match_levels(out, ref_dir, max_gain=14.0):
    """Raise or lower each converted effect to the average level of the file with the same name in ref_dir
    (the template's volumes were tuned for those), never boosting more than max_gain dB, peaks limited."""
    for name in SPEC:
        new, ref = os.path.join(out, name + ".mp3"), os.path.join(ref_dir, name + ".mp3")
        if not (os.path.exists(new) and os.path.exists(ref)):
            continue
        have, want = mean_db(new), mean_db(ref)
        if have is None or want is None:
            continue
        gain = max(-12.0, min(max_gain, want - have))
        tmp = new + ".tmp.mp3"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", new, "-af", f"volume={gain:.1f}dB,alimiter=limit=0.9", "-codec:a", "libmp3lame", "-b:a", "128k", tmp], check=True)
        os.replace(tmp, new)
        print(f"  level {name:17s} {have:6.1f} dB -> {mean_db(new):6.1f} dB (target {want:.1f})")


def main():
    if len(sys.argv) not in (2, 3, 4):
        sys.exit(__doc__)
    out = sys.argv[1]
    if "--levels-only" in sys.argv:
        match_levels(out, sys.argv[2])
        return
    raw = os.path.join(out, "raw")
    os.makedirs(raw, exist_ok=True)
    credits, report = [], []
    for name, (queries, lo, hi, want) in SPEC.items():
        cands = []
        for q in queries:
            try:
                results = search(q)
            except Exception as e:  # network / rate limit: keep going with what we have
                print(f"  {name}: search '{q}' failed: {e}", file=sys.stderr)
                results = []
            time.sleep(3.2)  # stay under 20 requests a minute
            for r in results:
                d = (r.get("duration") or 0) / 1000.0
                if not (lo <= d <= hi) or r.get("category") in ("pronunciation", "music", "podcast", "audiobook") or not r.get("url"):
                    continue
                words = set(re.findall(r"[a-z]+", ((r.get("title") or "") + " " + " ".join(t.get("name", "") for t in (r.get("tags") or []))).lower()))
                if not (words & MUST[name]) or (words & BAD.get(name, set())):
                    continue
                kw = set(re.findall(r"[a-z]+", q))
                title_hit = len(kw & set(re.findall(r"[a-z]+", (r.get("title") or "").lower())))
                cands.append((abs(d - want) - 0.4 * title_hit, r, d))
            if len(cands) >= 6:
                break
        cands.sort(key=lambda c: c[0])
        chosen = None
        for _, r, d in cands[:6]:
            ext = (r.get("filetype") or "mp3").replace("mp32", "mp3")
            path = os.path.join(raw, f"{name}-{r['id'][:8]}.{ext}")
            try:
                with get(r["url"]) as resp, open(path, "wb") as f:
                    f.write(resp.read(8_000_000))
            except Exception as e:
                print(f"  {name}: download failed ({r.get('title')}): {e}", file=sys.stderr)
                continue
            info = probe(path)
            if not info or info[1] < -45 or info[0] < lo * 0.8:   # unreadable, or nearly silent
                continue
            chosen = (r, d, path, info)
            break
        if not chosen:
            report.append(f"{name:17s} NOT FOUND (keep the stand-in)")
            continue
        r, d, path, info = chosen
        convert(path, os.path.join(out, name + ".mp3"), want, LEAD_SILENCE.get(name, 0))
        report.append(f"{name:17s} {d:4.1f}s  {r['license']:>4s}  {r.get('title','')[:40]!r}  by {r.get('creator') or '?'}")
        credits.append(f"- **{name}.mp3**: \"{r.get('title')}\" by {r.get('creator') or 'unknown'}, {r['license'].upper()} "
                       f"({r.get('license_url') or ''}), source: {r.get('foreign_landing_url') or r.get('detail_url')}")
    with open(os.path.join(out, "CREDITS.md"), "w", encoding="utf-8") as f:
        f.write("# Sound effect credits\n\nAll files are CC0 / public domain from Openverse (no attribution required; listed for the record).\n\n" + "\n".join(credits) + "\n")
    print("\n".join(report))
    if len(sys.argv) == 3:  # python3 fetch_sfx_openverse.py OUT REF_DIR
        match_levels(out, sys.argv[2])


if __name__ == "__main__":
    main()
