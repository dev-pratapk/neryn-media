#!/usr/bin/env python3
"""Build shorts/ep04-cine (Studio Kaveri · Rhea calls every lead back) — "Neryn Cinema" look.

Graded Pixabay footage (assets/clips), film-style subtitles, letterbox, few overlays. Run from comment-build/.
"""
import json
import os
import shutil

DST = "shorts/ep04-cine"
DUR = {k: v["dur"] for k, v in json.load(open("voice/ep04_el/durations.json", encoding="utf-8")).items()}
VO = {"k1": 2.6, "c1": 8.4, "k2": 15.2, "r1": 23.6, "p1": 28.4, "r2": 30.5, "k3": 36.8, "n1": 40.3, "cta": 46.2}
D = 54.0
TURN = 20.2

# clip, start, end, media offset
SHOTS = [("rain", 0.0, 4.6, 0.0), ("dash", 4.6, 7.0, 0.5), ("callday", 7.0, 14.2, 0.0), ("desk", 14.2, TURN, 0.0),
         ("table", 22.0, 27.5, 0.0), ("hands", 27.5, 35.8, 0.0), ("dash", 35.8, 39.8, 0.0), ("room", 39.8, 45.8, 0.0),
         ("rain", 45.8, D, 0.0)]

SUBS = [  # start, end, text
    (VO["k1"], VO["k1"] + DUR["k1"] + 0.3, "நாளைக்கு காலையில call பண்ணிக்கலாம்…"),
    (VO["c1"], VO["c1"] + 2.3, "Sorry sir, நேத்து ராத்திரியே வேற ஒருத்தர் call பண்ணாங்க."),
    (VO["c1"] + 2.4, VO["c1"] + DUR["c1"] + 0.3, "Already book பண்ணிட்டோம்."),
    (VO["k2"], VO["k2"] + 2.0, "Ad-க்கு காசு நான் கட்டுறேன்…"),
    (VO["k2"] + 2.1, VO["k2"] + DUR["k2"] + 0.3, "lead-அ வேற ஒருத்தன் எடுக்குறான்."),
    (VO["r1"], VO["r1"] + 2.3, "Hi! Studio Kaveri-ல இருந்து Rhea பேசுறேன்."),
    (VO["r1"] + 2.4, VO["r1"] + DUR["r1"] + 0.2, "இப்போ தான் உங்க form பாத்தேன்."),
    (VO["p1"], VO["p1"] + DUR["p1"] + 0.2, "அட, இப்போ தானே fill பண்ணேன்!"),
    (VO["r2"], VO["r2"] + DUR["r2"] + 0.3, "உங்க 2BHK-க்கு site visit, Saturday காலை 11 மணி ok-வா?"),
    (VO["k3"], VO["k3"] + DUR["k3"] + 0.3, "நான் தூங்கும் போதும் site visits book ஆகுது."),
    (VO["n1"], VO["n1"] + DUR["n1"] + 0.4, "Leads wait பண்ணாது. Rhea-வும் wait பண்ணாது."),
    (VO["cta"], VO["cta"] + 2.2, "உங்க ads-ல leads waste ஆகுதா?"),
    (VO["cta"] + 2.3, D - 2.4, "நாங்க fix பண்ணி தர்றோம். Comment-ல LEAD-னு போடுங்க."),
]

FX = [  # start, dur, name, vol
    (0.0, 10.0, "rain-car", 0.38), (1.0, 1.2, "phone-buzz", 0.55), (1.05, 1.0, "phone-buzz-chime", 0.25),
    (6.8, 8.0, "office-day", 0.45), (14.0, 6.2, "office-day", 0.35),
    (TURN, 2.5, "bass-hit", 0.7),
    (22.0, 12.0, "night-room", 0.35), (22.4, 0.8, "phone-ring", 0.45), (23.25, 0.8, "phone-ring", 0.4),
    (35.7, 12.0, "night-room", 0.25), (36.0, 1.4, "notify-soft", 0.45),
    (45.8, 8.2, "rain-car", 0.22), (VO["cta"] + 4.0, 0.25, "key-tap", 0.5), (VO["cta"] + 4.12, 0.25, "key-tap", 0.5),
    (VO["cta"] + 4.24, 0.25, "key-tap", 0.5), (VO["cta"] + 4.36, 0.25, "key-tap", 0.5), (D - 2.3, 1.4, "notify-soft", 0.3),
]

CSS = r"""
@font-face { font-family: "Anek Tamil"; src: url("assets/fonts/AnekTamil-tamil.woff2") format("woff2"); font-weight: 300 800; unicode-range: U+0964-0965, U+0B82-0BFA, U+200C-200D, U+20B9, U+25CC; }
@font-face { font-family: "Anek Tamil"; src: url("assets/fonts/AnekTamil-latin.woff2") format("woff2"); font-weight: 300 800; unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+2000-206F, U+20AC, U+2122, U+2190-2193, U+2212, U+2215, U+FEFF, U+FFFD; }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 1080px; height: 1920px; overflow: hidden; background: #000; }
#root { position: relative; width: 1080px; height: 1920px; overflow: hidden; background: #000; font-family: "Anek Tamil", sans-serif; color: #f4efe6; }
.shot { position: absolute; inset: 0; overflow: hidden; opacity: 0; }
.shot video { position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; }
#fade { position: absolute; inset: 0; background: #000; opacity: 0; }
.bar { position: absolute; left: 0; width: 1080px; height: 200px; background: #000; }
#barT { top: 0; } #barB { bottom: 0; }
.loc { position: absolute; left: 70px; top: 250px; font: 600 26px/1 "Anek Tamil"; letter-spacing: 0.22em; text-transform: uppercase; color: rgba(244,239,230,0.85); opacity: 0; }
.loc b { color: #f0a33a; font-weight: 700; }
.sub { position: absolute; left: 90px; width: 900px; top: 1440px; text-align: center; font: 600 46px/1.3 "Anek Tamil"; color: #fff; text-shadow: 0 2px 4px rgba(0,0,0,0.9), 0 0 24px rgba(0,0,0,0.6); text-wrap: balance; opacity: 0; }
.sub .nw { white-space: nowrap; }
.glass { position: absolute; border-radius: 34px; background: rgba(28,30,36,0.72); border: 1px solid rgba(255,255,255,0.14); box-shadow: 0 30px 60px rgba(0,0,0,0.45); backdrop-filter: blur(18px); opacity: 0; }
#noti { left: 70px; top: 330px; width: 940px; padding: 26px 30px; display: flex; gap: 22px; align-items: center; }
.ico { width: 76px; height: 76px; border-radius: 20px; display: grid; place-items: center; font: 800 34px/1 "Anek Tamil"; color: #141a26; background: #f0a33a; flex: none; padding-top: 4px; }
.glass small { display: block; font: 600 22px/1 "Anek Tamil"; letter-spacing: 0.12em; text-transform: uppercase; color: rgba(244,239,230,0.65); }
.glass b { display: block; margin-top: 10px; font: 650 36px/1.15 "Anek Tamil"; color: #fff; }
.glass span.t { margin-left: auto; align-self: flex-start; font: 500 22px/1 "Anek Tamil"; color: rgba(244,239,230,0.6); }
#title { position: absolute; left: 0; width: 1080px; top: 860px; text-align: center; font: 700 64px/1.2 "Anek Tamil"; color: #fff; opacity: 0; }
#title small { display: block; margin-top: 18px; font: 600 24px/1 "Anek Tamil"; letter-spacing: 0.3em; color: rgba(244,239,230,0.6); }
#bill { left: 600px; top: 330px; width: 410px; padding: 26px 28px; background: rgba(245,240,230,0.94); color: #141a26; transform: rotate(2.5deg); }
#bill small { color: #6b665c; }
#bill b { color: #141a26; font-size: 44px; }
#bill i { display: block; margin-top: 10px; font: 600 22px/1.2 "Anek Tamil"; font-style: normal; color: #b4472f; }
#never { position: absolute; left: 0; width: 1080px; top: 830px; text-align: center; font: 700 150px/1.3 "Anek Tamil"; color: #fff; opacity: 0; }
#form { left: 70px; top: 330px; width: 700px; padding: 22px 26px; display: flex; gap: 18px; align-items: center; }
#form .ico { background: #1f9d5c; color: #fff; width: 62px; height: 62px; font-size: 28px; }
#form b { font-size: 30px; }
#call { left: 180px; top: 760px; width: 720px; padding: 34px 36px; text-align: center; }
#call .av { width: 120px; height: 120px; margin: 0 auto; border-radius: 50%; background: #f0a33a; color: #141a26; font: 800 60px/128px "Anek Tamil"; }
#call b { font-size: 48px; margin-top: 18px; }
#call small { margin-top: 12px; }
#call .tm { display: block; margin-top: 16px; font: 600 28px/1 "Anek Tamil"; color: #7fe0a8; }
#cal { left: 140px; top: 330px; width: 800px; padding: 26px 30px; display: flex; gap: 22px; align-items: center; }
#cal .ico { background: #fff; color: #e5484d; font-size: 22px; line-height: 1.1; text-align: center; padding-top: 6px; }
#cal .ico em { display: block; font: 800 34px/1 "Anek Tamil"; font-style: normal; color: #141a26; }
#sig { position: absolute; left: 0; width: 1080px; top: 780px; text-align: center; opacity: 0; }
#sig b { display: block; font: 700 120px/1.1 "Anek Tamil"; color: #fff; letter-spacing: -0.01em; }
#sig { background: radial-gradient(60% 40% at 50% 45%, rgba(0,0,0,0.55), transparent 75%); padding: 120px 0; top: 660px; }
#sig small { display: block; margin-top: 26px; font: 600 34px/1.35 "Anek Tamil"; color: #fff; text-shadow: 0 2px 10px rgba(0,0,0,0.8); }
#sig b { text-shadow: 0 4px 20px rgba(0,0,0,0.6); }
#sig small span { color: #f0a33a; }
#cmt { left: 100px; top: 900px; width: 880px; padding: 28px 30px; display: flex; gap: 20px; align-items: center; }
#cmt .ca { width: 70px; height: 70px; border-radius: 50%; background: #efd3e4; color: #141a26; display: grid; place-items: center; font: 700 30px/1 "Anek Tamil"; padding-top: 3px; flex: none; }
#cmt .cf { flex: 1; height: 72px; border-radius: 36px; background: rgba(255,255,255,0.1); display: flex; align-items: center; padding: 0 28px; font: 700 36px/1 "Anek Tamil"; color: #fff; }
#cmt .car { width: 3px; height: 38px; background: #f0a33a; margin-left: 4px; }
#brand { position: absolute; left: 0; width: 1080px; top: 820px; text-align: center; opacity: 0; }
#brand b { display: block; font: 700 150px/1 "Anek Tamil"; color: #fff; letter-spacing: -0.02em; }
#brand b span { color: #ff3b2f; }
#brand small { display: block; margin-top: 26px; font: 600 30px/1 "Anek Tamil"; letter-spacing: 0.3em; color: rgba(244,239,230,0.7); }
#grain { position: absolute; inset: 0; pointer-events: none; background: radial-gradient(120% 80% at 50% 45%, transparent 55%, rgba(0,0,0,0.55) 100%); }
"""


def html():
    shots = []
    for i, (clip, a, b, off) in enumerate(SHOTS):
        shots.append(f'  <div class="shot" id="sh{i}"><video id="v{i}" class="clip" src="assets/clips/{clip}.mp4" data-start="{a}" '
                     f'data-duration="{round(b - a, 2)}" data-media-start="{off}" data-track-index="{1 + i}" muted playsinline></video></div>')
    subs = "\n".join(f'  <div class="sub" id="s{i}">' + _nw(t) + "</div>" for i, (_, _, t) in enumerate(SUBS))
    body = f"""
<div id="root" data-composition-id="main" data-start="0" data-duration="{D}" data-width="1080" data-height="1920">
{chr(10).join(shots)}
  <div id="grain" data-layout-ignore></div>
  <div id="fade" data-layout-ignore></div>
  <div class="loc" id="locA" data-layout-allow-occlusion>Anna Nagar · <b>9:12 PM</b></div>
  <div class="loc" id="locB" data-layout-allow-occlusion>மறுநாள் · <b>12:40 PM</b></div>
  <div class="loc" id="locE" data-layout-allow-occlusion>அதே வாரம் · <b>9:40 PM</b></div>
  <div class="glass" id="noti" data-layout-allow-occlusion><div class="ico">SK</div><div><small>Studio Kaveri · New lead</small><b>Priya R · 2BHK interior</b></div><span class="t">now</span></div>
  <div class="glass" id="bill" data-layout-allow-occlusion><small>Meta Ads · this month</small><b>₹2,00,000</b><i>300 leads · பாதிக்கு மேல call போகல</i></div>
  <div class="glass" id="form" data-layout-allow-occlusion><div class="ico">✓</div><div><small>Form submitted</small><b>Arun K · 2BHK · Velachery</b></div></div>
  <div class="glass" id="call" data-layout-allow-occlusion><div class="av">R</div><b>Rhea</b><small>Studio Kaveri · calling</small><span class="tm" id="tm">0:00</span></div>
  <div class="glass" id="cal" data-layout-allow-occlusion><div class="ico">SAT<em>21</em></div><div><small>Calendar · Studio Kaveri</small><b>Site visit · 11:00 AM ✓</b></div></div>
  <div id="title" data-layout-allow-occlusion></div>
  <div id="never" data-layout-allow-occlusion>இனி இல்ல.</div>
  <div id="sig" data-layout-allow-occlusion><b>Rhea</b><small>Studio Kaveri-க்காக <span>Neryn</span> build பண்ணது.</small></div>
  <div class="glass" id="cmt" data-layout-allow-occlusion><div class="ca">K</div><div class="cf"><span id="ct"></span><span class="car" id="cc"></span></div></div>
  <div id="brand" data-layout-allow-occlusion><b>Neryn<span>.</span></b><small>COMMENT → BUILD</small></div>
  <div class="bar" id="barT" data-layout-ignore></div>
  <div class="bar" id="barB" data-layout-ignore></div>
{subs}
  <!--AUDIO-->
  <div id="driver" class="clip" data-start="0" data-duration="{D}" data-track-index="0" style="position:absolute;width:1px;height:1px;opacity:0"></div>
</div>
"""
    sh = json.dumps([[a, b] for _, a, b, _ in SHOTS])
    sb = json.dumps([[a, b] for a, b, _ in SUBS])
    script = """
<script>
(function () {
  var D = __D__, SH = __SH__, SB = __SB__, T = __TURN__, VO = __VO__, DUR = __DUR__;
  var $ = function (id) { return document.getElementById(id); };
  var tl = gsap.timeline({ paused: true });
  var tm = $("tm"), ct = $("ct"), cc = $("cc");
  function frame() {
    var t = tl.time();
    var s = Math.max(0, Math.min(14, Math.floor(t - VO.r1 + 0.6)));
    tm.textContent = "0:" + (s < 10 ? "0" : "") + s;
    var tt = VO.cta + 4.0, n = t < tt ? 0 : Math.min(4, Math.ceil((t - tt) / 0.12));
    ct.textContent = "LEAD".slice(0, n); cc.style.opacity = (Math.floor(t * 2.4) % 2 === 0 || n) ? 1 : 0;
  }
  tl.to({ v: 0 }, { v: 1, duration: D, ease: "none", onUpdate: frame }, 0);
  // shots: hard cuts, slow push-in on every shot
  SH.forEach(function (s, i) {
    tl.set("#sh" + i, { opacity: 1 }, s[0]);
    tl.fromTo("#v" + i, { scale: 1.0 }, { scale: 1.08, duration: s[1] - s[0], ease: "none" }, s[0]);
    tl.set("#sh" + i, { opacity: 0 }, s[1]);
  });
  // letterbox: in for the opening and the ending, out in the middle
  tl.fromTo(["#barT", "#barB"], { scaleY: 1 }, { scaleY: 0.0, duration: 0.8, ease: "power2.inOut", transformOrigin: "50% 0%" }, 6.6);
  tl.fromTo(["#barT", "#barB"], { scaleY: 0 }, { scaleY: 1, duration: 0.8, ease: "power2.inOut" }, 39.6);
  // opening fade from black
  tl.fromTo("#fade", { opacity: 1 }, { opacity: 0, duration: 1.0, ease: "power1.out" }, 0);
  // A: the lead arrives, nobody calls
  tl.fromTo("#locA", { opacity: 0, x: -20 }, { opacity: 1, x: 0, duration: 0.6 }, 0.4);
  tl.fromTo("#noti", { opacity: 0, y: -40 }, { opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }, 1.0);
  tl.to(["#noti", "#locA"], { opacity: 0, duration: 0.4 }, 6.5);
  // B: next day
  tl.fromTo("#locB", { opacity: 0, x: -20 }, { opacity: 1, x: 0, duration: 0.5 }, 7.2);
  tl.to("#locB", { opacity: 0, duration: 0.4 }, 13.6);
  // C: the bill
  tl.fromTo("#bill", { opacity: 0, y: 30, rotation: 6 }, { opacity: 1, y: 0, rotation: 2.5, duration: 0.6, ease: "power3.out" }, 14.6);
  tl.to("#bill", { opacity: 0, duration: 0.3 }, T - 0.3);
  // D: the turn
  tl.set("#fade", { opacity: 1 }, T);
  tl.fromTo("#never", { opacity: 0, scale: 1.04 }, { opacity: 1, scale: 1, duration: 0.5, ease: "power2.out" }, T + 0.35);
  tl.to("#never", { opacity: 0, duration: 0.3 }, 21.7);
  tl.to("#fade", { opacity: 0, duration: 0.6 }, 22.0);
  // E: the same evening, a new lead is called back in seconds
  tl.fromTo("#locE", { opacity: 0, x: -20 }, { opacity: 1, x: 0, duration: 0.5 }, 22.3);
  tl.fromTo("#form", { opacity: 0, y: -30 }, { opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }, 22.4);
  tl.to(["#form", "#locE"], { opacity: 0, duration: 0.35 }, 27.3);
  tl.fromTo("#call", { opacity: 0, scale: 0.94 }, { opacity: 1, scale: 1, duration: 0.45, ease: "power3.out" }, VO.r1 - 0.4);
  tl.to("#call", { opacity: 0, duration: 0.4 }, 35.5);
  // F: the calendar fills
  tl.fromTo("#cal", { opacity: 0, y: -30 }, { opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }, 36.0);
  tl.to("#cal", { opacity: 0, duration: 0.4 }, 39.5);
  // G: signature
  tl.fromTo("#sig b", { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6, ease: "power3.out" }, 43.1);
  tl.fromTo("#sig", { opacity: 0 }, { opacity: 1, duration: 0.01 }, 43.1);
  tl.fromTo("#sig small", { opacity: 0 }, { opacity: 1, duration: 0.5 }, 43.6);
  tl.to("#sig", { opacity: 0, duration: 0.4 }, 45.6);
  // H: the ask
  tl.fromTo("#shtint", { opacity: 0 }, { opacity: 0, duration: 0.01 }, 0);
  tl.fromTo("#cmt", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }, VO.cta + 2.4);
  tl.to("#cmt", { opacity: 0, duration: 0.35 }, D - 2.55);
  tl.to("#fade", { opacity: 0.7, duration: 0.6 }, 45.8);
  tl.fromTo("#brand", { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6, ease: "power3.out" }, D - 2.3);
  // subtitles
  SB.forEach(function (s, i) {
    tl.fromTo("#s" + i, { opacity: 0 }, { opacity: 1, duration: 0.12 }, s[0] - 0.03);
    tl.to("#s" + i, { opacity: 0, duration: 0.12 }, s[1]);
  });
  window.__timelines = window.__timelines || {};
  window.__timelines["main"] = tl;
})();
</script>
"""
    for k, v in {"__D__": D, "__SH__": sh, "__SB__": sb, "__TURN__": TURN, "__VO__": json.dumps(VO), "__DUR__": json.dumps(DUR)}.items():
        script = script.replace(k, str(v))
    script = script.replace('  tl.fromTo("#shtint", { opacity: 0 }, { opacity: 0, duration: 0.01 }, 0);\n', "")
    return ('<!doctype html>\n<html lang="ta">\n<head>\n<meta charset="UTF-8" />\n<meta name="viewport" content="width=1080, height=1920" />\n'
            '<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>\n<style>' + CSS + "</style>\n</head>\n<body>"
            + body + script + "</body>\n</html>\n")


def _nw(t):
    import re
    return re.sub(r"(\S+-\S+)", r'<span class="nw">\1</span>', t)


os.makedirs(f"{DST}/assets/vo", exist_ok=True)
os.makedirs(f"{DST}/assets/fonts", exist_ok=True)
for f in os.listdir("shorts/ep02-v4/assets/fonts"):
    shutil.copy(f"shorts/ep02-v4/assets/fonts/{f}", f"{DST}/assets/fonts/{f}")
for k in VO:
    shutil.copy(f"voice/ep04_el/{k}.wav", f"{DST}/assets/vo/{k}.wav")
for f in ("hyperframes.json", "AGENTS.md", "CLAUDE.md"):
    shutil.copy(f"shorts/ep03-v4/{f}", f"{DST}/{f}")
open(f"{DST}/package.json", "w").write(open("shorts/ep03-v4/package.json").read().replace("ep03-v4", "ep04-cine"))
open(f"{DST}/meta.json", "w").write('{\n  "id": "ep04-cine",\n  "name": "ep04-cine",\n  "createdAt": "2026-11-18T16:30:00.000Z"\n}\n')
open(f"{DST}/index.html", "w", encoding="utf-8").write(html())
json.dump({"vo": [[k, s, DUR[k]] for k, s in VO.items()], "fx": [list(f) for f in FX]}, open("ep04/audio.json", "w"), indent=1)
print(f"wrote {DST}/index.html · {D} s")
