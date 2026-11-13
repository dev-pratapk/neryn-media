#!/usr/bin/env python3
"""Ep 03: build the voice-only preview and the script sheet from ep03/timing.json.

Run from comment-build/ after place_lines.py:
    python3 tools/ep03_preview.py
Writes ep03/ep03-voice-preview-v3.mp3 (call lines EQ'd like a phone line, stand-in ring at 0 s)
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
                "ep03/ep03-voice-preview-v3.mp3"], check=True)

NAMES = {"N": "Narrator (Prashant V)", "M": "Meera, owner (Indu)", "A": "AI receptionist (Nila)", "P": "Customer (Rajan)"}
SCREEN = {
    "open1": "Night. Closed outlet, shutter down, one lit phone. HUD: 11:40 PM · Shop closed. On-screen question from frame 1: \"கடை மூடியாச்சு. Call எடுத்தது யாரு?\"",
    "open2": "Live call waveform, order card starts filling: 1 kg chocolate · Anna Nagar",
    "open3": "Order card: ₹1,700 · WhatsApp link sent ✓",
    "who": "Camera pulls back: empty shop, chairs up. Big \"யாரு?\"",
    "rewind": "REWIND · last week. 4 outlet pins, one phone number, phones ringing",
    "hook": "Chips: 2 staff · ₹36,000 salary. Missed-call counter runs to 40. Flip board: ₹68,000 LOST",
    "stuck": "Two giant lines, tangles between chips",
    "build": "போதும். (0.65 s silence) → grid → kit: Tamil AI voice · 4 outlets · 24 hrs",
    "reveal": "Back to the 11:40 PM call card: the receptionist avatar flips to an \"AI\" badge. Chips: 24 hrs · 4 outlets",
    "free": "Day. Staff at the counter with customers; report card: Missed calls 0",
    "twist": "Giant \"AI\" behind the phone, strike through \"Human?\"",
    "meta": "Narrator's own waveform fills the screen, chip: \"இந்த voice-உம் AI\"",
    "human": "Every voice label flips to AI one by one; last card: \"Human: நீங்க 👆\"",
    "cta": "Card: \"AI Receptionist · built by Neryn\" → comment box types CALL. End lockup text: \"வேற problem? Comment பண்ணுங்க\"",
}
rows = [f"| {ln['start']:.1f}–{ln['end']:.1f} | {NAMES[d[ln['key']]['speaker']]} | {d[ln['key']]['text']} | {SCREEN[ln['key']]} |" for ln in t["lines"]]
turn = next(ln for ln in t["lines"] if ln["key"] == "build")["start"] - 0.65
md = f"""# Ep 03 · Bloom Cakes (4 outlets) — AI receptionist · script v3

**Strategy.** The proof comes first: the film opens on the AI taking an order in a closed shop at 11:40 PM, and asks who answered.
That question holds the viewer through the problem (salaries paid, calls still missed). The answer lands right after "போதும்.", then the
reveals escalate (the receptionist is AI → you couldn't tell → the narrator is AI → the only human is you) so attention peaks just
before the single call to action, which says plainly that Neryn builds this for the viewer's business.
The owner's line says what a mid-level owner needs to hear: staff aren't replaced, they go back to customers.

Mid-level business: 4 outlets, one order number, 2 phone staff (₹36,000 salary), 40 missed calls a week × ₹1,700 = ₹68,000.
Bloom Cakes and its numbers are a demo story, not a client case. CTA keyword: **CALL**. One CTA only; the "what should we build next?"
ask moves to the end card and pinned comment. No "free"/"tool" wording.

Length: {total} s · voice preview: `ep03-voice-preview-v3.mp3` (the call is EQ'd like a phone line; the ring is a stand-in).
All lines passed the ElevenLabs Scribe read-back (no dropped Tamil words).

| Time (s) | Speaker | Line | On screen |
|---|---|---|---|
""" + "\n".join(rows) + f"""

Silent turn: "போதும்." at {turn:.2f} s (0.65 s before "Okay.").
"""
open("ep03/SCRIPT_EP03.md", "w", encoding="utf-8").write(md)
print(f"wrote preview + script sheet · {total} s")
