#!/usr/bin/env python3
"""Ep 02 background music beds via ElevenLabs Music (instrumental).

Run from comment-build/:
    .venv/bin/python voice/gen_ep02_music_el.py            # both beds
    .venv/bin/python voice/gen_ep02_music_el.py day        # only this one

Two beds that follow the story: a quiet, uneasy night bed that stops dead at the "போதும்." cut, and a warm
"after" bed that starts as the narrator says "இதுக்கு ஒரு solution build பண்ணுவோம்" and runs to the end.
Writes voice/ep02_music/<name>.mp3 and prints the credits used.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "ep02_music")

from dotenv import load_dotenv  # noqa: E402
load_dotenv(os.path.join(ROOT, ".env"))
from elevenlabs.client import ElevenLabs  # noqa: E402

NO = ["vocals", "silence", "fade out", "outro", "ending before the last section"]
BEDS = {
    # night: sections follow the film beats from 0 s; the edit cuts it dead at the "போதும்." turn (20.37 s)
    "night": {
        "positive_global_styles": ["late-night uneasy background bed for voice-over", "soft low synth pad", "ticking clock-like pulse",
                                   "sparse muted veena plucks", "70 BPM", "restrained, mixed quiet"],
        "negative_global_styles": NO + ["drum kit", "bright tone", "busy arrangement"],
        "sections": [
            {"section_name": "Whisper", "duration_ms": 4700, "lines": [],
             "positive_local_styles": ["very soft pad", "faint ticking"], "negative_local_styles": NO},
            {"section_name": "Clock", "duration_ms": 5700, "lines": [],
             "positive_local_styles": ["steady ticking pulse", "occasional veena pluck"], "negative_local_styles": NO},
            {"section_name": "Numbers", "duration_ms": 6800, "lines": [],
             "positive_local_styles": ["low drone swelling", "tighter pulse", "darker harmony"], "negative_local_styles": NO},
            {"section_name": "Stuck", "duration_ms": 3800, "lines": [],
             "positive_local_styles": ["peak tension", "sustained to the very last moment", "no resolution"], "negative_local_styles": NO},
        ],
    },
    # day: starts at 21.81 s on "இதுக்கு ஒரு solution build பண்ணுவோம்" and runs to the end lockup
    "day": {
        "positive_global_styles": ["warm hopeful background bed for voice-over", "light acoustic guitar", "soft marimba",
                                   "gentle tabla-inspired groove", "100 BPM", "clean modern feel", "steady energy"],
        "negative_global_styles": NO + ["heavy drums", "EDM drop", "busy lead melody"],
        "sections": [
            {"section_name": "Spark", "duration_ms": 3000, "lines": [],
             "positive_local_styles": ["quick bright lift", "marimba pickup"], "negative_local_styles": NO},
            {"section_name": "Groove", "duration_ms": 9900, "lines": [],
             "positive_local_styles": ["light steady groove", "guitar and marimba"], "negative_local_styles": NO},
            {"section_name": "Twist", "duration_ms": 4800, "lines": [],
             "positive_local_styles": ["groove softens", "held warm chords"], "negative_local_styles": NO},
            {"section_name": "Relief", "duration_ms": 8200, "lines": [],
             "positive_local_styles": ["groove returns brighter", "gentle uplift"], "negative_local_styles": NO},
            {"section_name": "Call to action", "duration_ms": 7600, "lines": [],
             "positive_local_styles": ["steady groove", "same energy"], "negative_local_styles": NO},
            {"section_name": "Resolve", "duration_ms": 5000, "lines": [],
             "positive_local_styles": ["final resolved chord ringing to the very end"], "negative_local_styles": ["vocals", "silence"]},
        ],
    },
}

# the "போதும்." turn (20.37 s): a short Tamil-mass style hit, original composition (no film reference)
STING_NO = ["vocals", "slow intro", "build-up before the hit", "soft start", "silence at the start"]
BEDS["stinger_a"] = {
    "positive_global_styles": ["Tamil cinema mass hero-entry stinger", "huge thavil hit on the very first beat", "nadaswaram blast",
                               "deep sub impact", "short and punchy", "ring-out tail"],
    "negative_global_styles": STING_NO,
    "sections": [{"section_name": "Hit", "duration_ms": 3000, "lines": [],
                  "positive_local_styles": ["massive thavil and nadaswaram hit at 0 seconds", "then ring out"], "negative_local_styles": STING_NO}],
}
BEDS["stinger_b"] = {
    "positive_global_styles": ["Tamil mass action stinger", "thavil roll ending in one giant hit on the first beat", "brass stab",
                               "deep sub boom", "short and punchy", "ring-out tail"],
    "negative_global_styles": STING_NO,
    "sections": [{"section_name": "Hit", "duration_ms": 3000, "lines": [],
                  "positive_local_styles": ["giant hit right at the start", "brass and sub boom", "then ring out"], "negative_local_styles": STING_NO}],
}


def credits(c):
    s = c.user.subscription.get()
    return s.character_count


def main():
    os.makedirs(OUT, exist_ok=True)
    only = set(sys.argv[1:])
    c = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
    before = credits(c)
    for name, plan in BEDS.items():
        if only and name not in only:
            continue
        audio = c.music.compose(composition_plan=plan, respect_sections_durations=True, output_format="mp3_44100_192")
        path = os.path.join(OUT, name + ".mp3")
        with open(path + ".part", "wb") as f:
            for chunk in audio:
                f.write(chunk)
        os.replace(path + ".part", path)
        print(f"wrote {path}")
    print(f"credits used: {credits(c) - before}")


if __name__ == "__main__":
    main()
