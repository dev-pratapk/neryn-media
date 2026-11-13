#!/usr/bin/env python3
"""Read-back check of generated voice lines with ElevenLabs Scribe (replaces the Sarvam check).

Run from comment-build/:
    .venv/bin/python tools/stt_check_el.py voice/gen_ep02_vo_el.py            # every line
    .venv/bin/python tools/stt_check_el.py voice/gen_ep02_vo_el.py twist cta  # only these keys

For every line it transcribes voice/<epNN>_el/<key>.wav (Tamil, `tam`), prints the transcript next to the
script text, and flags a line when a Tamil word from the script has no close match in what was heard.
Scribe writes English words and numbers in Tamil letters (Sir -> சார், 9:40 -> ஒன்பது நாற்பது), so English
words and digits cannot be checked this way: listen to those yourself. Spelling variants in Tamil
(கேட்கவும் vs கேக்கவும்) are tolerated by a fuzzy match and are not flagged.
Needs ELEVENLABS_API_KEY in .env (read from the environment, never printed).
"""
import difflib
import importlib.util
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MODEL = os.environ.get("EL_STT_MODEL", "scribe_v3")


def load_lines(gen_path):
    spec = importlib.util.spec_from_file_location("gen", gen_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.LINES, mod.OUT


def norm(s):
    return re.sub(r"[^\w₹]+", " ", s.lower()).strip()


def tamil_tokens(text):
    """Tamil words of the script, without the English prefix of mixed tokens (auto-ஆ -> ஆ) and without very short ones."""
    out = []
    for w in re.sub(r"\[[^\]]*\]", " ", text).split():
        tam = "".join(re.findall(r"[\u0B80-\u0BFF]+", w))
        if len(tam) >= 3:
            out.append(tam)
    return out


def has_close(tok, heard_tokens, cutoff=0.7):
    return any(difflib.SequenceMatcher(None, tok, h).ratio() >= cutoff for h in heard_tokens)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    gen = sys.argv[1] if os.path.isabs(sys.argv[1]) else os.path.join(ROOT, sys.argv[1])
    only = set(sys.argv[2:])
    lines, out_dir = load_lines(gen)
    from elevenlabs.client import ElevenLabs
    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
    flagged = 0
    for key, spk, text in lines:
        if only and key not in only:
            continue
        wav = os.path.join(out_dir, key + ".wav")
        with open(wav, "rb") as f:
            res = client.speech_to_text.convert(file=f, model_id=MODEL, language_code="tam", tag_audio_events=False)
        heard = res.text.strip()
        want = re.sub(r"\[[^\]]*\]\s*", "", text)
        heard_tokens = ["".join(re.findall(r"[\u0B80-\u0BFF]+", w)) for w in heard.split()]
        heard_tokens = [h for h in heard_tokens if h]
        missing = [t for t in tamil_tokens(want) if not has_close(t, heard_tokens)]
        bad = bool(missing)
        flagged += bad
        print(f"[{'CHECK' if bad else ' ok  '}] {key} ({spk})")
        print(f"   script : {want}")
        print(f"   heard  : {heard}")
        if missing:
            print(f"   Tamil words not found in what was heard: {', '.join(missing)}")
    print(f"\n{flagged} line(s) need a listen." if flagged else "\nEvery Tamil word of every line was heard. (English words and numbers: listen yourself.)")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(os.path.join(ROOT, ".env"))
    main()
