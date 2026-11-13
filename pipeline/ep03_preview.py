#!/usr/bin/env python3
"""Ep 03: build the voice-only preview and the script sheet from ep03/timing.json.

Run from comment-build/ after place_lines.py:
    python3 tools/ep03_preview.py
Writes ep03/ep03-voice-preview-v4.mp3 (call lines EQ'd like a phone line, stand-in ring at 0 s)
and ep03/SCRIPT_EP03.md.
"""
import json
import subprocess

t = json.load(open("ep03/timing.json"))
d = json.load(open("voice/ep03_el/durations.json", encoding="utf-8"))
PHONE = {"open1", "open2", "open3"}

args, chains, labels = [], [], []
for i, ln in enumerate(t["lines"]):
    args += ["-i", f"voice/ep03_el/{ln['key']}.wav"]
    eq = ",highpass=f=320,lowpass=f=3400,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,volume=1.5dB" if ln["key"] in PHONE else ""
    chains.append(f"[{i}:a]aformat=channel_layouts=stereo,aresample=48000{eq},adelay={int(round(ln['start'] * 1000))}:all=1[a{i}]")
    labels.append(f"[a{i}]")
ring = ("sine=f=400:d=0.8:r=48000,tremolo=f=25:d=0.9,volume='if(lt(t,0.34),1,if(lt(t,0.46),0,1))':eval=frame,"
        "afade=t=in:d=0.02,afade=t=out:st=0.76:d=0.04,aformat=channel_layouts=stereo,volume=-14dB,adelay=50:all=1[ring]")
total = t["total"]
fc = (";".join(chains) + ";" + ring + ";" + "".join(labels)
      + f"[ring]amix=inputs={len(labels) + 1}:normalize=0,apad=whole_dur={total},atrim=0:{total},loudnorm=I=-16:TP=-1.5:LRA=11,alimiter=limit=0.84[out]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *args, "-filter_complex", fc, "-map", "[out]", "-c:a", "libmp3lame", "-b:a", "192k",
                "ep03/ep03-voice-preview-v4.mp3"], check=True)

NAMES = {"N": "Narrator (Prashant V)", "M": "Meera, owner (Ramaa)", "A": "Mithra, the voice agent (Nila)", "P": "Customer (Rajan)"}
SCREEN = {
    "open1": "Night. Closed outlet, shutter down, one lit phone. HUD: 11:40 PM · Shop closed. Question on screen from frame 1: \"கடை மூடியாச்சு. Call எடுத்தது யாரு?\"",
    "open2": "Live call waveform, caller card \"Mithra · Bloom Cakes\", order card starts filling: 1 kg chocolate · Anna Nagar",
    "open3": "Order card: ₹1,700 · WhatsApp link sent ✓",
    "who": "Camera pulls back: empty shop, chairs up. Big \"மித்ரா யாரு?\"",
    "rewind": "REWIND · last week. 4 outlet pins, one phone number, phones ringing",
    "hook": "Chips: 2 staff · ₹36,000 salary. Missed-call counter runs to 40. Flip board: ₹68,000 LOST",
    "stuck": "Two giant lines, tangles between chips",
    "build": "போதும். (0.65 s silence) → grid → kit: Tamil voice agent · 4 outlets · 24 hrs",
    "reveal": "Back to the 11:40 PM call card: Mithra's avatar flips to a \"Neryn Agent\" badge. Chips: 24 hrs · 4 outlets · தமிழ்",
    "free": "Day. Staff at the counter with customers; report card: Missed calls 0",
    "twist": "Giant \"மித்ரா\" behind the phone, strike through \"Human?\"",
    "meta": "Narrator's own waveform fills the screen, chip: \"இந்த voice-உம் Neryn agent\"",
    "human": "Every voice label flips to \"Agent\" one by one; last card: \"Human: நீங்க 👆\"",
    "cta": "Card: \"Mithra · Voice Agent · built by Neryn\" → comment box types CALL. End lockup text: \"வேற problem? Comment பண்ணுங்க\"",
}
rows = [f"| {ln['start']:.1f}–{ln['end']:.1f} | {NAMES[d[ln['key']]['speaker']]} | {d[ln['key']]['text']} | {SCREEN[ln['key']]} |" for ln in t["lines"]]
turn = next(ln for ln in t["lines"] if ln["key"] == "build")["start"] - 0.65
md = f"""# Ep 03 · Bloom Cakes (4 outlets) — "Mithra", a Neryn voice agent · script v4

**Strategy.** The proof comes first: the film opens on Mithra taking an order in a closed shop at 11:40 PM, and asks who she is.
That question holds the viewer through the problem (salaries paid, calls still missed). The answer lands right after "போதும்.":
Mithra isn't human, she's a Neryn agent. Then the reveals escalate (you couldn't tell → the narrator is an agent too → the only human
is you) so attention peaks just before the single call to action, which says plainly that Neryn builds a Mithra for the viewer's business.

**Naming.** The word "AI" is never spoken or shown. The product is a named agent ("Mithra · Voice Agent · built by Neryn"), which reads as
premium and gives owners something to ask for ("எங்களுக்கும் ஒரு மித்ரா"). "Human இல்ல" keeps it honest. The AI-voice disclosure stays where
the platforms require it (caption line and YouTube's altered-content setting), not in the script.

Mid-level business: 4 outlets, one order number, 2 phone staff (₹36,000 salary), 40 missed calls a week × ₹1,700 = ₹68,000.
Bloom Cakes and its numbers are a demo story, not a client case. CTA keyword: **CALL**. One CTA only; the "what should we build next?"
ask moves to the end card and pinned comment. The owner's line shows staff aren't replaced: they go back to customers.

**Voice tuning.** Three takes per line; the kept take is the one nearest that speaker's own middle pitch that isn't flat, so nobody
changes register between lines. All lines are levelled to the same loudness. Delivery tags steer tone (warm, curious, amused, relieved).

Length: {total} s · voice preview: `ep03-voice-preview-v4.mp3` (the call is EQ'd like a phone line; the ring is a stand-in).

| Time (s) | Speaker | Line | On screen |
|---|---|---|---|
""" + "\n".join(rows) + f"""

Silent turn: "போதும்." at {turn:.2f} s (0.65 s before "Okay.").
"""
open("ep03/SCRIPT_EP03.md", "w", encoding="utf-8").write(md)
print(f"wrote preview + script sheet · {total} s")
