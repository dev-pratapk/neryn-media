#!/usr/bin/env python3
"""Ep 03 (Bloom Cakes, 4 outlets: "Mithra", a Neryn voice agent) voice lines via ElevenLabs Eleven v4.

Run from comment-build/:
    .venv/bin/python voice/gen_ep03_vo_el.py                 # every line, 3 takes each, best take kept
    .venv/bin/python voice/gen_ep03_vo_el.py reveal cta      # only these keys
    TAKES=1 .venv/bin/python voice/gen_ep03_vo_el.py who     # single take

Tone tuning (script v4):
- every line is generated TAKES times; the kept take is the one closest to that speaker's target pitch
  (so a speaker doesn't jump register between lines) that also moves enough (not flat);
- delivery tags per line ([warmly], [curious], ...) steer the tone; they are not spoken;
- every kept line is levelled to the same average loudness.
Writes voice/ep03_el/<key>.wav (trimmed, 48 kHz), voice/ep03_el/takes/, and voice/ep03_el/durations.json.
"""
import json
import math
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "ep03_el")
sys.path.insert(0, os.path.join(ROOT, "tools"))

# load .env BEFORE importing elevenlabs (the SDK reads the key at import time)
from dotenv import load_dotenv  # noqa: E402
load_dotenv(os.path.join(ROOT, ".env"))
from elevenlabs import VoiceSettings  # noqa: E402
from elevenlabs.client import ElevenLabs  # noqa: E402
from voice_stats import stats  # noqa: E402

TAKES = int(os.environ.get("TAKES", "3"))
LEVEL_DB = -23.0

# speaker: voice id, target median pitch (Hz), minimum pitch movement (semitones), speed
SPEAKER = {
    "N": ("yIFUVClxedWzoMYhk15k", 180, 3.4, 1.03),  # Prashant V, narrator
    "M": ("ZhJ5LanYnCmLKQUXvsV7", 200, 3.0, 1.0),   # Ramaa, Meera (owner, Bloom Cakes): sits lower than Mithra, sounds more senior
    "A": ("C2RGMrNBTZaNfddRPeRH", 232, 3.8, 1.0),   # Nila, "Mithra" the voice agent
    "P": ("NsQE1nARp8lz1QelRCh9", 150, 3.2, 1.0),   # Rajan, customer
}

LINES = [
    # v4: the agent has a name (Mithra); the word "AI" is never spoken. Open on her call in a closed shop.
    ("open1",  "A", "[warmly] வணக்கம்! Bloom Cakes, நான் மித்ரா. சொல்லுங்க?"),
    ("open2",  "P", "நாளைக்கு 1 kg chocolate cake வேணும். Anna Nagar-ல pick-up பண்றேன்."),
    ("open3",  "A", "[cheerfully] சூப்பர்! ₹1,700. Link WhatsApp-ல அனுப்புறேன்."),
    ("who",    "N", "[curious] கடை மூடியாச்சு. அப்போ… மித்ரா யாரு?"),
    ("rewind", "N", "போன வாரம், இதே கடை. 4 outlets, ஒரே number."),
    ("hook",   "N", "2 staff, ₹36,000 salary. இருந்தும் 40 missed calls. ₹68,000 போச்சு!"),
    ("stuck",  "N", "இன்னொரு ஆள் வச்சா salary. வைக்கலன்னா loss."),
    ("build",  "N", "Okay. இதுக்கு ஒரு solution build பண்ணுவோம்."),
    ("reveal", "N", "மித்ரா… human இல்ல. Neryn agent."),
    ("free",   "M", "[relieved] Calls-அ மித்ரா பாத்துக்குறாங்க. Customers-அ நம்ம staff பாத்துக்குறாங்க!"),
    ("twist",  "N", "பாத்தீங்களா? Human இல்லன்னு கண்டுபிடிக்கவே முடியல."),
    ("meta",   "N", "இவ்ளோ ஏன்… இவ்வளவு நேரம் பேசின நானும் ஒரு agent தான்."),
    ("human",  "N", "இந்த video-ல human… நீங்க மட்டும் தான்."),
    ("cta",    "N", "உங்க business-க்கும் ஒரு மித்ரா, நாங்க build பண்ணி தர்றோம். Comment-ல CALL-னு போடுங்க!"),
]


def score(s, target, min_move):
    """Lower is better: semitones away from the speaker's target pitch, plus a penalty for flat delivery."""
    off = abs(12 * math.log2(s["f0"] / target))
    flat = max(0.0, min_move - s["spread"]) * 2.0
    return off + flat


def main():
    takes_dir = os.path.join(OUT, "takes")
    os.makedirs(takes_dir, exist_ok=True)
    only = set(sys.argv[1:])
    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
    dpath = os.path.join(OUT, "durations.json")
    durs = json.load(open(dpath, encoding="utf-8")) if os.path.exists(dpath) else {}
    trim = "silenceremove=start_periods=1:start_threshold=-42dB:start_silence=0.02"

    # pass 1: generate the takes
    takes = {}  # key -> [(wav, stats)]
    for key, spk, text in LINES:
        if only and key not in only:
            continue
        voice, _, _, speed = SPEAKER[spk]
        for n in range(TAKES):
            mp3 = os.path.join(takes_dir, f"{key}_{n}.mp3")
            wav = os.path.join(takes_dir, f"{key}_{n}.wav")
            audio = client.text_to_speech.convert(
                voice, text=text, model_id="eleven_v4", language_code="ta", output_format="mp3_44100_128",
                voice_settings=VoiceSettings(stability=0.5, similarity_boost=0.8, speed=speed))
            with open(mp3, "wb") as f:
                for chunk in audio:
                    f.write(chunk)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp3, "-ar", "48000", "-ac", "1",
                            "-af", f"{trim},areverse,{trim},areverse", wav], check=True)
            os.remove(mp3)
            s = stats(wav)
            if s:
                takes.setdefault(key, []).append((wav, s))
                print(f"  {key}_{n}: pitch {s['f0']:.0f} Hz, movement {s['spread']:.1f} st, {s['dur']:.2f} s", flush=True)

    # pass 2: per speaker, the target pitch is the middle of everything that speaker produced (this run's takes
    # plus lines kept earlier), so every line of one speaker sits in the same register
    spk_of = {k: sp for k, sp, _ in LINES}
    text_of = {k: t for k, _, t in LINES}
    for key, cands in takes.items():
        spk = spk_of[key]
        _, fallback, min_move, _ = SPEAKER[spk]
        pool = [s["f0"] for k, cs in takes.items() if spk_of[k] == spk for _, s in cs]
        pool += [d["pitch_hz"] for k, d in durs.items() if k not in takes and d.get("speaker") == spk and "take" in d and k in spk_of]
        target = sorted(pool)[len(pool) // 2] if len(pool) >= 3 else fallback
        sc, wav, s = min(((score(s, target, min_move), w, s) for w, s in cands), key=lambda c: c[0])
        gain = max(-9.0, min(9.0, LEVEL_DB - s["level"]))
        final = os.path.join(OUT, key + ".wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wav, "-af", f"volume={gain:.2f}dB,alimiter=limit=0.89", "-ar", "48000", final], check=True)
        durs[key] = {"dur": round(s["dur"], 3), "speaker": spk, "text": re.sub(r"\[[^\]]*\]\s*", "", text_of[key]),
                     "pitch_hz": round(s["f0"]), "movement_st": round(s["spread"], 1), "take": os.path.basename(wav)}
        print(f"{key:6s} {spk} target {target:.0f} Hz -> kept {os.path.basename(wav)}: {s['f0']:.0f} Hz, {s['spread']:.1f} st, {s['dur']:.2f}s", flush=True)
    json.dump(durs, open(dpath, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
