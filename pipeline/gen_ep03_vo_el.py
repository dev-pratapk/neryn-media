#!/usr/bin/env python3
"""Ep 03 (Bloom Cakes, 4 outlets: AI receptionist) voice lines via ElevenLabs Eleven v4.

Run from comment-build/:
    .venv/bin/python voice/gen_ep03_vo_el.py            # every line
    .venv/bin/python voice/gen_ep03_vo_el.py twist cta  # only these keys

Writes voice/ep03_el/<key>.wav (trimmed, 48 kHz) and voice/ep03_el/durations.json.
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "ep03_el")

# load .env BEFORE importing elevenlabs (the SDK reads the key at import time)
from dotenv import load_dotenv  # noqa: E402
load_dotenv(os.path.join(ROOT, ".env"))
from elevenlabs.client import ElevenLabs  # noqa: E402

VOICE = {
    "N": "yIFUVClxedWzoMYhk15k",  # Prashant V, narrator
    "M": "WGcwqLckKl7a8wkVgPAc",  # Indu, Meera (owner, Bloom Cakes)
    "S": "ZhJ5LanYnCmLKQUXvsV7",  # Ramaa, Revathi (staff on the phones)
    "A": "C2RGMrNBTZaNfddRPeRH",  # Nila, the AI receptionist
    "P": "NsQE1nARp8lz1QelRCh9",  # Rajan, customer
}

LINES = [
    ("cold",  "S", "[nervous] Sir, hold-ல இருங்க… madam, ஒரு நிமிஷம்…"),
    ("clock", "N", "சனிக்கிழமை ராத்திரி 8:40. Bloom Cakes-ஓட 4 outlets-க்கும் ஒரே number."),
    ("hook",  "N", "2 staff, ₹36,000 salary. இருந்தும் 40 missed calls. ₹68,000 போச்சு!"),
    ("stuck", "N", "இன்னொரு ஆள் வச்சா salary. வைக்கலன்னா loss."),
    ("build", "N", "Okay. இதுக்கு ஒரு solution build பண்ணுவோம்."),
    ("f1",    "N", "இனிமே எல்லா outlet call-உம் AI தான் எடுக்கும்."),
    ("ai1",   "A", "வணக்கம்! Bloom Cakes. எந்த outlet-ல pick-up பண்றீங்க?"),
    ("cust",  "P", "Anna Nagar. நாளைக்கு 1 kg chocolate, \"Happy Birthday Diya\"."),
    ("ai2",   "A", "சூப்பர்! ₹1,700. Advance link WhatsApp-ல அனுப்புறேன்."),
    ("twist", "N", "பாத்தீங்களா? இது AI-னு கண்டுபிடிக்கவே முடியல."),
    ("meta",  "N", "இவ்ளோ ஏன்… இவ்வளவு நேரம் பேசின நானே ஒரு AI தான்."),
    ("free",  "M", "[sighs] இப்போ staff phone-அ இல்ல… customers-அ கவனிக்கிறாங்க!"),
    ("cta",   "N", "உங்க business-க்கும் AI receptionist வேணும்னா, comment-ல CALL-னு போடுங்க!"),
    ("next",  "N", "அடுத்து என்ன build பண்ணணும்? உங்க problem-அ comment பண்ணுங்க!"),
]


def wav_duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True, check=True).stdout
    return round(float(out.strip()), 3)


def main():
    os.makedirs(OUT, exist_ok=True)
    only = set(sys.argv[1:])
    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
    dpath = os.path.join(OUT, "durations.json")
    durs = json.load(open(dpath, encoding="utf-8")) if os.path.exists(dpath) else {}
    for key, spk, text in LINES:
        if only and key not in only:
            continue
        mp3 = os.path.join(OUT, key + ".mp3")
        wav = os.path.join(OUT, key + ".wav")
        audio = client.text_to_speech.convert(
            VOICE[spk], text=text, model_id="eleven_v4", language_code="ta", output_format="mp3_44100_128")
        with open(mp3, "wb") as f:
            for chunk in audio:
                f.write(chunk)
        trim = "silenceremove=start_periods=1:start_threshold=-42dB:start_silence=0.02"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp3, "-ar", "48000", "-ac", "1",
                        "-af", f"{trim},areverse,{trim},areverse", wav], check=True)
        os.remove(mp3)
        durs[key] = {"dur": wav_duration(wav), "speaker": spk, "text": re.sub(r"\[[^\]]*\]\s*", "", text)}
        print(f"{key:6s} {spk} {durs[key]['dur']:6.2f}s  {durs[key]['text'][:60]}")
    json.dump(durs, open(dpath, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
