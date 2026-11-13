#!/usr/bin/env python3
"""Build shorts/ep03-v4/index.html (Bloom Cakes · Mithra, a Neryn voice agent).

Run from comment-build/ after place_lines.py wrote ep03/timing.json:
    python3 tools/build_ep03.py

Reuses the v4 story-world CSS from the Ep 01 template; the scenes and timeline are new. Every cue is written
relative to the voice lines in timing.json (S(key) = line start, P(key, i) = start of its i-th phrase), so
regenerating a voice line only needs a rebuild. Also prepares assets (voice with phone EQ on the call, sound
effects, ring) and audio.json.
"""
import json
import os
import re
import shutil
import subprocess

SKILL = os.path.expanduser("~/.claude/skills/neryn-episode")
DST = "shorts/ep03-v4"
timing = json.load(open("ep03/timing.json"))
D = timing["total"]
css = re.search(r"<style>(.*?)</style>", open(os.path.join(SKILL, "assets/template/episode-index.html"), encoding="utf-8").read(), re.S).group(1)

EXTRA_CSS = r"""
/* ---------- Ep 03 additions ---------- */
#q1 { position: absolute; left: 60px; top: 316px; font: 700 42px/1.2 var(--font); color: var(--amber); white-space: nowrap; }
#rw { position: absolute; left: 60px; top: 316px; font: 700 42px/1.2 var(--font); color: var(--amber); white-space: nowrap; opacity: 0; }
#nphone { left: 300px; top: 404px; }
.scr.call { background: linear-gradient(180deg, #14262f, #0b1319); color: #fff; }
.call .sb { background: transparent; }
.call .ct { position: absolute; left: 0; right: 0; top: 92px; text-align: center; font: 600 19px/1 var(--font); letter-spacing: 0.16em; color: #9cc0ba; }
.call .cav { position: absolute; left: 163px; top: 132px; width: 130px; height: 130px; border-radius: 50%; background: #f2b35e; color: var(--teal); font: 800 66px/138px var(--font); text-align: center; }
.call .cbadge { position: absolute; left: 88px; top: 160px; width: 280px; height: 76px; border-radius: 38px; background: var(--amber); color: var(--ink); font: 800 25px/82px var(--font); letter-spacing: 0.12em; text-align: center; opacity: 0; }
.call .cn { position: absolute; left: 0; right: 0; top: 284px; text-align: center; font: 700 44px/1 var(--font); }
.call .cs { position: absolute; left: 0; right: 0; top: 340px; text-align: center; font: 500 22px/1 var(--font); color: #a9bfbb; }
.call .tmr { position: absolute; left: 0; right: 0; top: 378px; text-align: center; font: 600 24px/1 var(--font); color: #7fe0a8; }
.call .wv { position: absolute; left: 52px; right: 52px; top: 428px; height: 76px; display: flex; align-items: center; justify-content: space-between; }
.call .wv i { display: block; width: 8px; height: 100%; border-radius: 4px; background: #7fe0a8; }
.call .tr { position: absolute; left: 20px; right: 20px; top: 532px; display: flex; flex-direction: column; gap: 12px; }
.call .tb { max-width: 370px; padding: 12px 16px 8px; border-radius: 18px; font: 600 21px/1.3 var(--font); background: rgba(255,255,255,0.12); align-self: flex-start; opacity: 0; }
.call .tb.c { align-self: flex-end; background: rgba(127,224,168,0.2); }
.call .end { position: absolute; left: 188px; bottom: 34px; width: 80px; height: 80px; border-radius: 50%; background: #e5484d; }
#cs1 { left: 30px; top: 700px; } #cs2 { left: 690px; top: 560px; }
#co1 { left: 20px; top: 1010px; } #co2 { left: 700px; top: 900px; } #co3 { left: 660px; top: 1130px; }
.stk { font-size: 60px; }
#who0 { top: 700px; color: #f2ede3; font-size: 86px; }
#who1 { top: 600px; color: var(--amber); font-size: 200px; line-height: 1.25; }
#who2 { top: 860px; color: #f2ede3; font-size: 150px; }
#stk1 { top: 700px; } #stk2 { top: 810px; }
#outs { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; opacity: 0; }
.oc { position: absolute; width: 410px; height: 230px; border-radius: 30px; background: rgba(24,27,36,0.96); border: 1px solid rgba(255,255,255,0.10); box-shadow: 0 30px 60px rgba(0,0,0,0.5); padding: 30px; color: #f1ece2; opacity: 0; }
.oc i { display: grid; place-items: center; width: 64px; height: 64px; border-radius: 18px; font: 700 32px/1 var(--font); font-style: normal; color: #fff; padding-top: 4px; }
.oc b { display: block; margin-top: 22px; font: 650 40px/1 var(--font); }
.oc small { display: block; margin-top: 12px; font: 600 20px/1 var(--font); letter-spacing: 0.12em; text-transform: uppercase; color: #a49d90; }
.oc em { position: absolute; right: 26px; top: 30px; padding: 12px 18px 8px; border-radius: 999px; background: rgba(239,90,70,0.16); color: #ff7a66; font: 700 22px/1 var(--font); font-style: normal; letter-spacing: 0.08em; opacity: 0; }
#oc1 { left: 110px; top: 420px; } #oc2 { left: 560px; top: 420px; } #oc3 { left: 110px; top: 690px; } #oc4 { left: 560px; top: 690px; }
#cnum { left: 330px; top: 980px; } #chA { left: 60px; top: 1120px; } #chB { left: 590px; top: 1120px; } #chC { left: 330px; top: 1262px; }
#board { top: 560px; }
#giant { top: 300px; font-size: 240px; height: 300px; }
#dphone { left: 300px; top: 540px; }
#meta { position: absolute; left: 70px; width: 940px; top: 470px; color: var(--ink); }
#meta .me { font: 700 60px/1.2 var(--font); color: #5f5b53; opacity: 0; }
#meta .mc { position: relative; margin-top: 40px; height: 250px; border-radius: 40px; background: #fff; box-shadow: 0 40px 90px rgba(20,26,38,0.14); padding: 34px 40px; opacity: 0; }
#meta .mc small { display: block; font: 600 22px/1 var(--font); letter-spacing: 0.16em; color: #5f5b53; }
#meta .wv { position: absolute; left: 40px; right: 40px; top: 84px; height: 130px; display: flex; align-items: center; justify-content: space-between; }
#meta .wv i { display: block; width: 12px; height: 100%; border-radius: 6px; background: var(--ink); }
#meta .mp { position: absolute; right: 36px; top: 24px; height: 46px; padding: 0 22px; border-radius: 23px; display: grid; place-items: center; font: 700 20px/1 var(--font); letter-spacing: 0.14em; padding-top: 3px; }
#meta .mp1 { background: rgba(20,26,38,0.08); color: #5f5b53; }
#meta .mp2 { background: var(--amber); color: var(--ink); opacity: 0; }
#meta .m2 { margin-top: 44px; font: 700 92px/1.2 var(--font); color: var(--ink); text-wrap: balance; opacity: 0; }
#meta .m2 span { color: #b86f0c; }
#cast { position: absolute; left: 80px; top: 400px; width: 920px; height: 730px; border-radius: 40px; background: #fff; box-shadow: 0 40px 90px rgba(20,26,38,0.14); padding: 36px 44px; opacity: 0; }
#cast .lh small { color: #5f5b53; }
#cast .pp { background: rgba(20,26,38,0.07); color: #5f5b53; }
#cast .pd { background: rgba(240,163,58,0.22); color: #7a4a05; }
#you { position: relative; height: 112px; margin: 14px -20px 0; padding: 0 20px; display: flex; align-items: center; gap: 22px; border-radius: 26px; background: var(--amber); opacity: 0; }
#you .la { width: 64px; height: 64px; border-radius: 50%; background: var(--ink); color: #fff; display: grid; place-items: center; font: 700 28px/1 var(--font); padding-top: 3px; }
#you .ln { font: 700 42px/1 var(--font); color: var(--ink); }
#you .hp { margin-left: auto; height: 52px; padding: 0 24px; border-radius: 26px; background: var(--ink); color: #fff; display: grid; place-items: center; font: 700 22px/1 var(--font); letter-spacing: 0.14em; padding-top: 3px; }
#tool .free { color: var(--ink); font-size: 24px; }
#prof .lk { color: var(--ink); }
#tw .t2 { font-size: 84px; color: #b86f0c; }
#list .lh small { color: #5f5b53; }
#lmore { font-weight: 600; color: var(--ink); }
#endb small.s2 { margin-top: 26px; letter-spacing: 0.04em; font: 600 34px/1.2 var(--font); color: var(--ink); }
#eyB { position: absolute; left: 0; top: 0; white-space: nowrap; opacity: 0; }
#tmB { opacity: 0; }
.cap.d em { color: #9c610c; }
"""

BODY = r"""
<div id="root" data-composition-id="main" data-start="0" data-duration="__D__" data-width="1080" data-height="1920">

  <div class="scene" id="night">
    <div id="nbg" data-layout-ignore></div>
    <div id="ncam" data-layout-ignore>
      <div id="outs">
        <div class="oc" id="oc1"><i style="background:#2b8f86">A</i><b>Anna Nagar</b><small>Outlet 1</small><em>missed 12</em></div>
        <div class="oc" id="oc2"><i style="background:#c9862a">T</i><b>T. Nagar</b><small>Outlet 2</small><em>missed 10</em></div>
        <div class="oc" id="oc3"><i style="background:#7a5cc2">V</i><b>Velachery</b><small>Outlet 3</small><em>missed 9</em></div>
        <div class="oc" id="oc4"><i style="background:#3d7bd9">A</i><b>Adyar</b><small>Outlet 4</small><em>missed 9</em></div>
      </div>
      <div class="chip n" id="cnum" data-layout-allow-occlusion><i style="background:#25a35a">☎</i><div><small>Order line</small><b>4 outlets · ஒரே number</b></div></div>
      <div class="chip n" id="chA" data-layout-allow-occlusion><i style="background:#2b8f86">2</i><div><small>Phone-க்கு மட்டும்</small><b>2 staff</b></div></div>
      <div class="chip n" id="chB" data-layout-allow-occlusion><i style="background:#c9862a">₹</i><div><small>Salary · month</small><b>₹36,000</b></div></div>
      <div class="chip n" id="chC" data-layout-allow-occlusion><i style="background:var(--coral)">!</i><div><small>Missed calls · week</small><b><span id="n40">0</span> calls</b></div></div>
      <svg id="tangle">
        <path id="tg1" pathLength="1" d="M250 1120 C 120 1010, 60 900, 180 790 C 300 690, 80 640, 150 560"/>
        <path id="tg2" pathLength="1" d="M800 1120 C 990 1030, 1010 930, 900 840 C 800 760, 1000 680, 930 600"/>
        <path id="tg3" pathLength="1" d="M520 1262 C 420 1180, 640 1120, 540 1040 C 470 980, 600 950, 560 915"/>
        <circle id="td1" cx="560" cy="915" r="7"/>
      </svg>
      <div class="stk" id="stk1" data-layout-allow-occlusion>இன்னொரு ஆள் வச்சா salary.</div>
      <div class="stk" id="stk2" data-layout-allow-occlusion>வைக்கலன்னா loss.</div>
      <div id="q1" data-layout-allow-occlusion>கடை மூடியாச்சு. Call எடுத்தது யாரு?</div>
      <div id="rw" data-layout-allow-occlusion>◀◀ REWIND · போன சனிக்கிழமை</div>
      <div class="phone" id="nphone" data-layout-allow-occlusion>
        <div class="scr call">
          <div class="isl"></div>
          <div class="sb"><span>11:40</span><span>5G</span></div>
          <div class="ct">INCOMING · BLOOM CAKES</div>
          <div class="cav">M</div>
          <div class="cn">Mithra</div>
          <div class="cs">Bloom Cakes · on call</div>
          <div class="tmr" id="tmrN">00:00</div>
          <div class="wv" id="wvN"></div>
          <div class="tr">
            <div class="tb" id="tb1">வணக்கம்! Bloom Cakes, நான் மித்ரா.</div>
            <div class="tb c" id="tb2">1 kg chocolate cake · Anna Nagar pick-up</div>
            <div class="tb" id="tb3">₹1,700 · Link WhatsApp-ல ✓</div>
          </div>
          <div class="end"></div>
        </div>
      </div>
      <div class="chip n" id="cs1" data-layout-allow-occlusion><i style="background:var(--coral)">✕</i><div><small>Shutter</small><b>Closed · 9:30 PM</b></div></div>
      <div class="chip n" id="cs2" data-layout-allow-occlusion><i style="background:#5b5f6b">0</i><div><small>Staff in shop</small><b>யாரும் இல்ல</b></div></div>
      <div class="chip n" id="co1" data-layout-allow-occlusion><i style="background:#c9862a">1</i><div><small>Order</small><b>1 kg chocolate</b></div></div>
      <div class="chip n" id="co2" data-layout-allow-occlusion><i style="background:#2b8f86">A</i><div><small>Pick-up</small><b>Anna Nagar</b></div></div>
      <div class="chip n" id="co3" data-layout-allow-occlusion><i style="background:#25a35a">✓</i><div><small>₹1,700</small><b>Link sent</b></div></div>
      <div class="stk" id="who0" data-layout-allow-occlusion>கடை மூடியாச்சு.</div>
      <div class="stk" id="who1" data-layout-allow-occlusion>மித்ரா</div>
      <div class="stk" id="who2" data-layout-allow-occlusion>யாரு?</div>
    </div>
    <div id="lamp" data-layout-ignore></div>
    <div id="nvig" data-layout-ignore></div>
    <div id="board" data-layout-allow-occlusion>
      <div class="blab">Lost this week · missed calls</div>
      <div class="flap" id="bflap"></div>
      <div class="flap sm" id="pflap"></div>
      <div id="bfoot">40 calls × ₹1,700</div>
    </div>
  </div>

  <div class="scene" id="day">
    <div id="dbg" data-layout-ignore></div>
    <div id="grid" data-layout-ignore></div>
    <div id="enough" data-layout-allow-occlusion><b>போதும்.</b><small>ENOUGH.</small></div>
    <div id="kit" data-layout-allow-occlusion>
      <svg><rect id="kframe" pathLength="1" x="36" y="56" width="1008" height="378" rx="48"/></svg>
      <div class="klab">Neryn · Voice agent</div>
      <div class="kt" id="kt1" style="left:60px"><div class="ki" style="background:var(--teal)">அ</div><div class="kl">Tamil voice</div><div class="ks">Natural, polite</div></div>
      <div class="kt" id="kt2" style="left:395px"><div class="ki" style="background:var(--amber);color:var(--ink)">4</div><div class="kl">4 outlets</div><div class="ks">One number</div></div>
      <div class="kt" id="kt3" style="left:730px"><div class="ki" style="background:var(--green)">24</div><div class="kl">24 hours</div><div class="ks">Never misses</div></div>
    </div>
    <div id="a1" data-layout-ignore>
      <div id="giant"><span>மி</span><span>த்</span><span>ரா</span></div>
      <div class="phone" id="dphone" data-layout-allow-occlusion>
        <div class="scr call">
          <div class="isl"></div>
          <div class="sb"><span>11:40</span><span>5G</span></div>
          <div class="ct">BLOOM CAKES · ORDER LINE</div>
          <div class="cav" id="cavD">M</div>
          <div class="cbadge" id="cbD">NERYN AGENT</div>
          <div class="cn">Mithra</div>
          <div class="cs">Bloom Cakes · on call</div>
          <div class="tmr">00:12</div>
          <div class="wv" id="wvD"></div>
          <div class="tr">
            <div class="tb" style="opacity:1">வணக்கம்! Bloom Cakes, நான் மித்ரா.</div>
            <div class="tb c" style="opacity:1">1 kg chocolate cake · Anna Nagar pick-up</div>
            <div class="tb" style="opacity:1">₹1,700 · Link WhatsApp-ல ✓</div>
          </div>
          <div class="end"></div>
        </div>
      </div>
      <div class="chip d" id="cd1" data-layout-allow-occlusion><i style="background:var(--amber);color:var(--ink)">M</i><div><small>Mithra</small><b>Human இல்ல</b></div></div>
      <div class="chip d" id="cd2" data-layout-allow-occlusion><i style="background:var(--green)">24</i><div><small>On duty</small><b>24 hrs</b></div></div>
      <div class="chip d" id="cd3" data-layout-allow-occlusion><i style="background:var(--teal)">4</i><div><small>Outlets</small><b>ஒரே number</b></div></div>
      <div class="chip d" id="cd4" data-layout-allow-occlusion><i style="background:var(--teal)">அ</i><div><small>Speaks</small><b>தமிழ்</b></div></div>
    </div>
    <div id="tw" data-layout-allow-occlusion>
      <div class="te">பாத்தீங்களா?</div>
      <div class="t1"><span class="ig">Human<i class="strike"></i></span> இல்லன்னு</div>
      <div class="t2">கண்டுபிடிக்கவே முடியல.</div>
    </div>
    <div id="list" data-layout-allow-occlusion style="height:650px">
      <div class="lh"><div><small><span class="h1">MISSED CALLS · THIS WEEK</span><span class="h2">ALL ANSWERED ✓</span></small><b>Call report</b></div><div class="flap" id="lflap"></div></div>
      <div id="lrows"></div>
      <div id="lmore">Staff இப்போ counter-ல, customers கூட.</div>
    </div>
    <div id="toast" data-layout-allow-occlusion><i>✓</i><div><b>Mithra answered every call</b><small>4 outlets · 24 hrs</small></div></div>
    <div id="meta" data-layout-allow-occlusion>
      <div class="me">இவ்ளோ ஏன்…</div>
      <div class="mc"><small>NARRATOR · இந்த VOICE</small><div class="mp mp1">HUMAN?</div><div class="mp mp2">NERYN AGENT ✓</div><div class="wv" id="wvM"></div></div>
      <div class="m2">நானும் ஒரு <span>agent</span> தான்.</div>
    </div>
    <div id="cast" data-layout-allow-occlusion>
      <div class="lh"><div><small>இந்த VIDEO-ல</small><b>யாரு human?</b></div></div>
      <div id="crows"></div>
      <div id="you"><div class="la">♥</div><div class="ln">நீங்க</div><div class="hp">HUMAN ✓</div></div>
    </div>
    <div id="tool" data-layout-allow-occlusion>
      <div class="tr"><div class="ti">M</div><div><b>Mithra</b><small>Voice Agent · built by Neryn</small></div></div>
      <div class="free">NERYN AGENT</div>
      <div class="fe"><span>தமிழ்-ல பேசும்</span><span>4 outlets</span><span>24 hrs</span></div>
    </div>
    <div id="prof" data-layout-allow-occlusion><div class="pa">N<span>.</span></div><div><b>@neryn.pro</b><small>Comment → Build</small></div><div class="lk">நாங்க build பண்றோம்<b id="lrip"></b></div></div>
    <div id="cmt" data-layout-allow-occlusion>
      <div class="cl">COMMENTS</div>
      <div class="cr"><div class="ca">M</div><div class="cf"><span id="ctyped"></span><span class="car" id="ccaret"></span><span class="ph" id="cphd">Add a comment…</span></div><div class="cs"></div>
        <div class="cp"><small>@meera.bloomcakes · now</small><b>CALL</b><em>♥ 1</em></div></div>
    </div>
    <div id="endv" data-layout-ignore></div>
    <div id="endb" data-layout-allow-occlusion><b>Neryn<span>.</span></b><small>COMMENT → BUILD</small><small class="s2">வேற problem? Comment பண்ணுங்க.</small></div>
  </div>

  <div class="brand" id="brN" data-layout-ignore>Neryn<span>.</span></div>
  <div class="brand" id="brD" data-layout-ignore>Neryn<span>.</span></div>
  <div class="ep" id="epN" data-layout-ignore>EP 03 · CALL</div>
  <div class="ep" id="epD" data-layout-ignore>EP 03 · CALL</div>
  <div class="hud" id="hudN" data-layout-ignore>
    <div class="ey" id="eyA"><i style="background:var(--coral)"></i>Tonight · Shop closed</div>
    <div class="ey" id="eyB"><i style="background:var(--coral)"></i>Before · Rush hour</div>
    <div class="tm"><span id="tmA">11:40 PM</span><span id="tmB">8:40 PM</span></div>
  </div>
  <div class="hud" id="hudD" data-layout-ignore><div class="ey"><i style="background:var(--green)"></i>After · Shop closed</div><div class="tm"><span id="tmC">11:40 PM</span></div></div>

  <div id="caps"></div>
  <!--AUDIO-->
  <div id="driver" class="clip" data-start="0" data-duration="__D__" data-track-index="0" style="position:absolute;width:1px;height:1px;opacity:0"></div>
</div>
"""

SCRIPT = r"""
<script>
(function () {
  var TM = __TIMING__;
  var D = TM.total, LN = {};
  TM.lines.forEach(function (l) { LN[l.key] = l; });
  function S(k) { return LN[k].start; }
  function E(k) { return LN[k].end; }
  function P(k, i) { return LN[k].phrases[i][0]; }
  var $ = function (id) { return document.getElementById(id); };
  var T = S("build") - 0.65;              // the turn: "போதும்."

  // grid
  for (var gx = 90; gx < 1080; gx += 90) { var v = document.createElement("div"); v.className = "gv"; v.style.left = gx + "px"; $("grid").appendChild(v); }
  for (var gy = 90; gy < 1920; gy += 90) { var h = document.createElement("div"); h.className = "gh"; h.style.top = gy + "px"; $("grid").appendChild(h); }

  // waveforms
  function bars(id, n) { var out = []; for (var i = 0; i < n; i++) { var b = document.createElement("i"); $(id).appendChild(b); out.push(b); } return out; }
  var WN = bars("wvN", 22), WD = bars("wvD", 22), WM = bars("wvM", 34);

  // call report rows + cast rows
  [["Anna Nagar", "#f6d9a8", "12 calls"], ["T. Nagar", "#cfe3f6", "10 calls"], ["Velachery", "#e3dcf6", "9 calls"], ["Adyar", "#d8ecd2", "9 calls"]].forEach(function (r, i) {
    var d = document.createElement("div"); d.className = "lr"; d.id = "lr" + i;
    d.innerHTML = '<div class="fl"></div><div class="la" style="background:' + r[1] + '">' + r[0][0] + '</div><div class="ln">' + r[0] + '</div><div class="lm">' + r[2] + '</div><div class="pill pp">MISSED</div><div class="pill pd">ANSWERED ✓</div>';
    $("lrows").appendChild(d);
  });
  [["Mithra", "#f6d9a8", "Receptionist"], ["Customer", "#cfe3f6", "Caller"], ["Meera", "#efd3e4", "Owner"], ["Narrator", "#d8ecd2", "இந்த voice"]].forEach(function (r, i) {
    var d = document.createElement("div"); d.className = "lr"; d.id = "cr" + i;
    d.innerHTML = '<div class="fl"></div><div class="la" style="background:' + r[1] + '">' + r[0][0] + '</div><div class="ln">' + r[0] + '</div><div class="lm">' + r[2] + '</div><div class="pill pp">VOICE</div><div class="pill pd">AGENT ✓</div>';
    $("crows").appendChild(d);
  });

  // captions: [id, start, end, text, speaker label, night?]
  var CAPS = [
    [1, S("open1"), E("open1"), "வணக்கம்! Bloom Cakes, நான் மித்ரா. சொல்லுங்க?", "Mithra", 1],
    [2, P("open2", 0), LN.open2.phrases[0][1], "நாளைக்கு 1 kg chocolate cake வேணும்.", "Customer", 1],
    [3, P("open2", 1), E("open2"), "Anna Nagar-ல pick-up பண்றேன்.", "Customer", 1],
    [4, S("open3"), E("open3"), "சூப்பர்! ₹1,700. Link WhatsApp-ல அனுப்புறேன்.", "Mithra", 1],
    [5, P("rewind", 0), LN.rewind.phrases[1][1], "போன வாரம், இதே கடை.", "", 1],
    [6, P("rewind", 2), E("rewind"), "4 outlets, ஒரே number.", "", 1],
    [7, P("hook", 0), LN.hook.phrases[1][1], "2 staff, ₹36,000 salary.", "", 1],
    [8, P("hook", 2), LN.hook.phrases[3][1], "இருந்தும் 40 missed calls.", "", 1],
    [9, P("hook", 4), E("hook"), "₹68,000 போச்சு!", "", 1],
    [10, P("build", 0), LN.build.phrases[0][1], "Okay.", "", 0],
    [11, P("build", 1), E("build"), "இதுக்கு ஒரு solution build பண்ணுவோம்.", "", 0],
    [12, S("reveal"), E("reveal"), "மித்ரா… human இல்ல. Neryn agent.", "", 0],
    [13, P("free", 0), LN.free.phrases[0][1], "Calls-அ மித்ரா பாத்துக்குறாங்க.", "Meera · Owner", 0],
    [14, P("free", 1), E("free"), "Customers-அ நம்ம staff பாத்துக்குறாங்க!", "Meera · Owner", 0],
    [15, S("human"), E("human"), "இந்த video-ல human… நீங்க மட்டும் தான்.", "", 0],
    [16, P("cta", 0), LN.cta.phrases[0][1], "உங்க business-க்கும் ஒரு மித்ரா,", "", 0],
    [17, P("cta", 1), LN.cta.phrases[1][1], "நாங்க build பண்ணி தர்றோம்.", "", 0],
    [18, P("cta", 2), D, "Comment-ல CALL-னு போடுங்க!", "", 0]
  ];
  CAPS.forEach(function (c) {
    var d = document.createElement("div"); d.className = "cap " + (c[5] ? "n" : "d"); d.id = "cp" + c[0];
    d.innerHTML = (c[4] ? "<em>" + c[4] + "</em>" : "") + c[3].replace(/(\S+-\S+)/g, '<span class="nw">$1</span>'); $("caps").appendChild(d);
  });

  // split-flap boards
  var DIG = "0123456789", ABC = "ABCDEFGHIJKLMNOPRSTUVWXYZ";
  function makeFlap(el, init, keys) {
    var tiles = [];
    for (var i = 0; i < init.length; i++) { var t = document.createElement("div"); t.className = "ft"; t.innerHTML = '<span class="c"></span>'; el.appendChild(t); tiles.push(t.firstChild); }
    return { tiles: tiles, init: init, keys: keys };
  }
  function flapAt(set, t) {
    set.tiles.forEach(function (c, i) {
      var ch = set.init[i], sc = 1;
      set.keys.forEach(function (k, ki) {
        if (k.text[i] === ch && t >= k.t) return;
        var t0 = k.t + i * k.stagger, n = k.n + (i % 3), dt = t - t0;
        if (dt < 0) return;
        var idx = Math.floor(dt / k.step);
        if (idx >= n) { ch = k.text[i]; var dd = dt - n * k.step; sc = dd < k.step ? 1 - 0.75 * Math.sin(dd / k.step * Math.PI) : 1; }
        else { ch = k.pool[(i * 3 + idx * 7 + ki * 5) % k.pool.length]; sc = 1 - 0.75 * Math.sin((dt % k.step) / k.step * Math.PI); }
      });
      if (c.textContent !== ch) c.textContent = ch;
      c.style.transform = "scaleY(" + sc.toFixed(3) + ")";
    });
  }
  var tBoard = P("hook", 4) - 0.1, tRep = S("free");
  var FLAPS = [
    makeFlap($("bflap"), "       ", [{ t: tBoard + 0.15, text: "₹68,000", n: 5, step: 0.07, stagger: 0.08, pool: DIG }]),
    makeFlap($("pflap"), "       ", [{ t: tBoard + 0.85, text: "LOST   ", n: 3, step: 0.06, stagger: 0.05, pool: ABC }]),
    makeFlap($("lflap"), "     40", [{ t: tRep + 0.85, text: "     28", n: 4, step: 0.06, stagger: 0.04, pool: DIG }, { t: tRep + 1.45, text: "     18", n: 4, step: 0.06, stagger: 0.04, pool: DIG },
                                      { t: tRep + 2.55, text: "      9", n: 4, step: 0.06, stagger: 0.04, pool: DIG }, { t: tRep + 3.15, text: "      0", n: 4, step: 0.06, stagger: 0.04, pool: DIG }])
  ];

  var N = { s: 1, j: 1 }, ncam = $("ncam"), tmrN = $("tmrN"), ctyped = $("ctyped"), cphd = $("cphd"), ccaret = $("ccaret");
  var tType = P("cta", 2) + 0.15;
  var CALL = [[S("open1"), E("open1")], [S("open2"), E("open2")], [S("open3"), E("open3")]];
  function wave(list, t, on, base) {
    for (var k = 0; k < list.length; k++) {
      var a = on ? 0.22 + 0.78 * Math.abs(Math.sin(t * 9.1 + k * 1.7) * Math.sin(t * 3.3 + k * 0.63)) : base;
      list[k].style.transform = "scaleY(" + a.toFixed(3) + ")";
    }
  }
  var tl = gsap.timeline({ paused: true });
  function frame() {
    var t = tl.time();
    var x = (5 * Math.sin(t * 1.9) + 3 * Math.sin(t * 4.7 + 1.3)) * N.j, y = (4 * Math.sin(t * 1.4 + 0.7) + 2 * Math.sin(t * 5.9)) * N.j;
    var r = (0.45 * Math.sin(t * 1.15) + 0.2 * Math.sin(t * 3.3 + 0.4)) * N.j;
    ncam.style.transform = "translate(" + x.toFixed(2) + "px," + y.toFixed(2) + "px) rotate(" + r.toFixed(3) + "deg) scale(" + N.s.toFixed(4) + ")";
    FLAPS.forEach(function (f) { flapAt(f, t); });
    var sec = Math.max(0, Math.min(12, Math.floor(t - S("open1"))));
    tmrN.textContent = "00:" + (sec < 10 ? "0" : "") + sec;
    var talking = false; CALL.forEach(function (w) { if (t >= w[0] && t <= w[1]) talking = true; });
    wave(WN, t, talking, 0.12);
    wave(WD, t, t >= S("reveal") && t <= E("reveal"), 0.16);
    wave(WM, t, t >= S("meta") && t <= E("meta"), 0.14);
    var blink = Math.floor(t * 2.4) % 2 === 0;
    var cs = t < tType ? "" : "CALL".slice(0, Math.min(4, Math.ceil((t - tType) / 0.1)));
    ctyped.textContent = cs; cphd.style.display = cs ? "none" : "inline"; ccaret.style.opacity = (blink || cs) ? 1 : 0;
  }
  tl.to({ v: 0 }, { v: 1, duration: D, ease: "none", onUpdate: frame }, 0);
  var pop = function (sel, at, rot) {
    tl.fromTo(sel, { opacity: 0, scale: 0.85, rotation: (rot || 0) * 2, y: 16 }, { opacity: 1, scale: 1, rotation: rot || 0, y: 0, duration: 0.45, ease: "back.out(1.8)" }, at);
  };
  var rise = function (sel, at, dy) { tl.fromTo(sel, { opacity: 0, y: dy || 40 }, { opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }, at); };

  // ---- cold open: a call is answered in a closed shop (0 - who) ----
  var tWho = S("who"), tAsk = P("who", 3) - 0.08, tRw = S("rewind") - 0.12;
  tl.to("#lamp", { keyframes: [{ opacity: 0.6, duration: 0.05 }, { opacity: 1, duration: 0.1 }, { opacity: 0.8, duration: 0.08 }, { opacity: 1, duration: 0.2 }] }, 0.05);
  tl.fromTo("#nphone", { y: 0, scale: 1, rotation: -2 }, { y: -12, scale: 1, rotation: -1, duration: tWho, ease: "none" }, 0);
  tl.to(N, { s: 1.03, duration: tWho, ease: "sine.inOut" }, 0);
  pop("#cs1", 0.3, -5); pop("#cs2", 0.6, 4);
  tl.fromTo("#tb1", { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.3, ease: "power2.out" }, S("open1") + 0.1);
  tl.fromTo("#tb2", { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.3, ease: "power2.out" }, S("open2") + 0.1);
  tl.fromTo("#tb3", { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.3, ease: "power2.out" }, S("open3") + 0.1);
  pop("#co1", P("open2", 0) + 1.0, -4); pop("#co2", P("open2", 1) + 0.1, 4); pop("#co3", P("open3", 2), -3);

  // ---- who answered? (who - rewind) ----
  tl.fromTo("#nphone", { filter: "blur(0px) brightness(1)" }, { filter: "blur(9px) brightness(0.38)", duration: 0.45, ease: "power2.out" }, tWho);
  tl.to(["#cs1", "#cs2", "#co1", "#co2", "#co3", "#q1"], { opacity: 0, y: -16, duration: 0.3, ease: "power2.in" }, tWho);
  rise("#who0", tWho + 0.05);
  tl.to("#who0", { opacity: 0, y: -30, duration: 0.25, ease: "power2.in" }, tAsk - 0.3);
  tl.fromTo("#who1", { opacity: 0, scale: 1.25 }, { opacity: 1, scale: 1, duration: 0.4, ease: "power3.out" }, tAsk);
  rise("#who2", tAsk + 0.3);
  tl.to(N, { s: 1.07, duration: tRw - tWho, ease: "sine.inOut" }, tWho);

  // ---- rewind: last Saturday, 4 outlets, one number (rewind - hook) ----
  tl.to("#nphone", { y: 1700, rotation: -8, duration: 0.45, ease: "power3.in" }, tRw);
  tl.to(["#who1", "#who2"], { opacity: 0, x: 220, duration: 0.3, ease: "power2.in" }, tRw);
  tl.to(N, { s: 1.0, duration: 0.5, ease: "power2.inOut" }, tRw);
  rise("#rw", tRw + 0.15, 20);
  tl.to("#eyA", { opacity: 0, duration: 0.2 }, tRw + 0.15);
  tl.fromTo("#eyB", { opacity: 0 }, { opacity: 1, duration: 0.25 }, tRw + 0.2);
  tl.to("#tmA", { yPercent: -100, opacity: 0, duration: 0.3, ease: "power2.in" }, tRw + 0.15);
  tl.fromTo("#tmB", { yPercent: 100, opacity: 1 }, { yPercent: 0, opacity: 1, duration: 0.4, ease: "power3.out" }, tRw + 0.25);
  tl.set("#outs", { opacity: 1 }, tRw + 0.3);
  ["#oc1", "#oc2", "#oc3", "#oc4"].forEach(function (o, i) { pop(o, P("rewind", 2) - 0.25 + i * 0.15, i % 2 ? 2 : -2); });
  pop("#cnum", P("rewind", 3) - 0.05);

  // ---- the stakes (hook - stuck) ----
  var tMiss = P("hook", 3) - 0.05;
  pop("#chA", P("hook", 0), -3); pop("#chB", P("hook", 1), 3);
  pop("#chC", tMiss);
  var cnt = { v: 0 };
  tl.to(cnt, { v: 40, duration: 0.8, ease: "power1.inOut", onUpdate: function () { $("n40").textContent = Math.round(cnt.v); } }, tMiss);
  tl.fromTo(".oc em", { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)", stagger: 0.12 }, tMiss + 0.05);
  tl.to(N, { s: 1.06, duration: tBoard - S("hook"), ease: "sine.inOut" }, S("hook"));
  tl.fromTo("#outs", { filter: "blur(0px) brightness(1)" }, { filter: "blur(7px) brightness(0.45)", duration: 0.4, ease: "power2.out" }, tBoard - 0.1);
  tl.to(["#cnum", "#chA", "#chB", "#chC", "#rw"], { opacity: 0, y: -16, duration: 0.3, ease: "power2.in" }, tBoard - 0.15);
  tl.fromTo("#board", { opacity: 0, y: -70, scale: 0.96 }, { opacity: 1, y: 0, scale: 1, duration: 0.5, ease: "power3.out" }, tBoard);
  tl.fromTo("#bfoot", { opacity: 0 }, { opacity: 1, duration: 0.4 }, tBoard + 1.0);

  // ---- stuck (stuck - turn) ----
  var tSt = S("stuck") - 0.12;
  tl.to("#board", { y: 160, opacity: 0, duration: 0.32, ease: "power2.in" }, tSt - 0.1);
  tl.to(N, { s: 1.0, duration: 0.6, ease: "power2.inOut" }, tSt);
  rise("#stk1", tSt + 0.08);
  rise("#stk2", P("stuck", 1) - 0.08);
  pop("#chA", tSt + 0.3, -5); pop("#chB", tSt + 0.6, 4); pop("#chC", tSt + 0.9, -3);
  tl.fromTo("#tg1", { strokeDashoffset: 1.1 }, { strokeDashoffset: 0, duration: 0.9, ease: "power1.inOut" }, tSt + 0.4);
  tl.fromTo("#tg2", { strokeDashoffset: 1.1 }, { strokeDashoffset: 0, duration: 0.8, ease: "power1.inOut" }, tSt + 0.7);
  tl.fromTo("#tg3", { strokeDashoffset: 1.1 }, { strokeDashoffset: 0, duration: 0.8, ease: "power1.inOut" }, tSt + 1.0);
  tl.fromTo("#td1", { opacity: 0 }, { opacity: 1, duration: 0.2 }, tSt + 1.8);
  tl.to(N, { j: 2.2, duration: T - (tSt + 1.2), ease: "sine.in" }, tSt + 1.2);

  // ---- the turn: one word, then the build ----
  tl.set("#night", { autoAlpha: 0 }, T);
  tl.set("#day", { autoAlpha: 1 }, T);
  tl.set(["#hudN", "#brN", "#epN"], { opacity: 0 }, T);
  tl.set(["#brD", "#epD"], { opacity: 1 }, T);
  tl.fromTo("#enough", { scale: 1.06 }, { scale: 1, duration: 0.7, ease: "power2.out" }, T);
  tl.to("#enough", { y: -470, scale: 0.42, duration: 0.6, ease: "power3.inOut" }, T + 0.9);
  tl.to("#enough small", { opacity: 0, duration: 0.2 }, T + 0.9);
  tl.fromTo(".gv", { scaleY: 0 }, { scaleY: 1, duration: 0.7, ease: "power3.out", stagger: { each: 0.035, from: "center" } }, T + 0.85);
  tl.fromTo(".gh", { scaleX: 0 }, { scaleX: 1, duration: 0.7, ease: "power3.out", stagger: { each: 0.02, from: "center" } }, T + 0.9);
  tl.fromTo("#kit .klab", { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.35, ease: "power2.out" }, T + 1.35);
  tl.fromTo("#kt1", { opacity: 0, x: -520, rotation: -14 }, { opacity: 1, x: 0, rotation: 0, duration: 0.45, ease: "power4.out" }, T + 1.4);
  tl.fromTo("#kt2", { opacity: 0, y: 700, rotation: 8 }, { opacity: 1, y: 0, rotation: 0, duration: 0.45, ease: "power4.out" }, T + 1.7);
  tl.fromTo("#kt3", { opacity: 0, x: 520, rotation: 14 }, { opacity: 1, x: 0, rotation: 0, duration: 0.45, ease: "power4.out" }, T + 2.0);
  tl.fromTo("#kframe", { strokeDashoffset: 1.1 }, { strokeDashoffset: 0, duration: 0.55, ease: "power2.inOut" }, T + 2.25);
  tl.to(["#kit", "#enough"], { opacity: 0, scale: 1.25, filter: "blur(14px)", duration: 0.32, ease: "power3.in" }, T + 2.95);

  // ---- the reveal: Mithra isn't human ----
  var tA = T + 3.25, tNot = P("reveal", 1), tAg = P("reveal", 2);
  rise("#hudD", tA, 12);
  tl.fromTo("#giant span", { yPercent: 70, opacity: 0 }, { yPercent: 0, opacity: 1, duration: 0.6, ease: "power3.out", stagger: 0.1 }, tA);
  tl.fromTo("#dphone", { y: 1500, scale: 0.9 }, { y: 0, scale: 0.9, duration: 0.7, ease: "power3.out" }, tA + 0.05);
  tl.to("#cavD", { scale: 0, opacity: 0, duration: 0.18, ease: "power2.in" }, tNot);
  tl.fromTo("#cbD", { opacity: 0, scale: 1.5 }, { opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2.2)" }, tNot + 0.15);
  [["#cd1", 60, 640, tNot + 0.1], ["#cd2", 720, 780, tAg - 0.3], ["#cd3", 60, 1010, tAg + 0.1], ["#cd4", 720, 1130, tAg + 0.45]].forEach(function (c) {
    tl.fromTo(c[0], { opacity: 0, scale: 0.5, x: 540 - (c[1] + 150), y: 960 - (c[2] + 40) }, { opacity: 1, scale: 1, x: 0, y: 0, duration: 0.55, ease: "power3.out" }, c[3]);
  });

  // ---- the owner: calls are handled, staff are with customers ----
  tl.to("#a1", { x: -1080, duration: 0.38, ease: "power3.in" }, tRep - 0.15);
  tl.fromTo("#list", { opacity: 0, x: 1080 }, { opacity: 1, x: 0, duration: 0.55, ease: "power3.out" }, tRep - 0.05);
  tl.fromTo("#toast", { opacity: 0, y: -140 }, { opacity: 1, y: 0, duration: 0.5, ease: "back.out(1.4)" }, tRep + 0.1);
  [[0, 0.8], [1, 1.4], [2, 2.5], [3, 3.1]].forEach(function (p) {
    var r = "#lr" + p[0], at = tRep + p[1];
    tl.to(r + " .pp", { opacity: 0, scale: 0.8, duration: 0.15 }, at);
    tl.fromTo(r + " .pd", { opacity: 0, scale: 1.4 }, { opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2.2)" }, at);
    tl.fromTo(r + " .fl", { opacity: 0 }, { keyframes: [{ opacity: 1, duration: 0.15 }, { opacity: 0.45, duration: 0.6 }] }, at);
  });
  tl.fromTo("#lmore", { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.35, ease: "power2.out" }, P("free", 1));
  tl.to("#list .h1", { opacity: 0, duration: 0.2 }, tRep + 3.4);
  tl.fromTo("#list .h2", { opacity: 0 }, { opacity: 1, duration: 0.25 }, tRep + 3.4);
  var tTw = S("twist");
  tl.to(["#list", "#toast", "#hudD"], { opacity: 0, y: -40, duration: 0.3, ease: "power2.in" }, tTw - 0.2);

  // ---- you couldn't tell ----
  tl.fromTo("#tw .te", { opacity: 0, x: 120 }, { opacity: 1, x: 0, duration: 0.45, ease: "power3.out" }, tTw);
  rise("#tw .t1", P("twist", 1) - 0.05);
  tl.fromTo("#tw .strike", { scaleX: 0 }, { scaleX: 1, duration: 0.35, ease: "power2.inOut" }, P("twist", 1) + 0.5);
  rise("#tw .t2", P("twist", 1) + 0.85);
  var tMe = S("meta");
  tl.to("#tw", { x: -1080, duration: 0.36, ease: "power3.in" }, tMe - 0.18);

  // ---- the narrator is an agent too ----
  tl.fromTo("#meta .me", { opacity: 0, x: 120 }, { opacity: 1, x: 0, duration: 0.45, ease: "power3.out" }, tMe);
  rise("#meta .mc", tMe + 0.35);
  rise("#meta .m2", P("meta", 1) + 0.75);
  tl.to("#meta .mp1", { opacity: 0, scale: 0.8, duration: 0.15 }, P("meta", 1) + 1.5);
  tl.fromTo("#meta .mp2", { opacity: 0, scale: 1.5 }, { opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2.2)" }, P("meta", 1) + 1.5);
  var tHu = S("human");
  tl.to("#meta", { x: -1080, duration: 0.36, ease: "power3.in" }, tHu - 0.18);

  // ---- the only human is you ----
  tl.fromTo("#cast", { opacity: 0, x: 1080 }, { opacity: 1, x: 0, duration: 0.5, ease: "power3.out" }, tHu - 0.08);
  [0, 1, 2, 3].forEach(function (i) {
    var r = "#cr" + i, at = tHu + 0.3 + i * 0.28;
    tl.to(r + " .pp", { opacity: 0, scale: 0.8, duration: 0.12 }, at);
    tl.fromTo(r + " .pd", { opacity: 0, scale: 1.4 }, { opacity: 1, scale: 1, duration: 0.25, ease: "back.out(2.2)" }, at);
  });
  tl.fromTo("#you", { opacity: 0, scale: 0.8, y: 30 }, { opacity: 1, scale: 1, y: 0, duration: 0.45, ease: "back.out(2)" }, P("human", 1) - 0.05);
  var tC = S("cta");
  tl.to("#cast", { opacity: 0, y: -50, duration: 0.3, ease: "power2.in" }, tC - 0.2);

  // ---- we build one for you: comment CALL ----
  rise("#tool", tC, 60);
  tl.fromTo("#tool .free", { opacity: 0, scale: 1.6, rotation: -12 }, { opacity: 1, scale: 1, rotation: -4, duration: 0.4, ease: "back.out(2)" }, tC + 0.7);
  rise("#prof", P("cta", 1) - 0.05, 60);
  tl.fromTo("#lrip", { opacity: 0.8, scale: 0.2 }, { opacity: 0, scale: 1.6, duration: 0.55, ease: "power2.out" }, P("cta", 1) + 0.5);
  rise("#cmt", P("cta", 2) - 0.25, 60);
  tl.to("#cmt .cf", { opacity: 0, duration: 0.15 }, tType + 0.55);
  tl.fromTo("#cmt .cp", { opacity: 0 }, { opacity: 1, duration: 0.25 }, tType + 0.55);
  var tEnd = E("cta") - 0.05;
  tl.to(["#tool", "#prof", "#cmt"], { opacity: 0, y: -60, duration: 0.3, ease: "power2.in", stagger: 0.04 }, tEnd - 0.05);
  tl.fromTo("#endv", { opacity: 0 }, { opacity: 1, duration: 0.35 }, tEnd);
  tl.fromTo("#endb", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }, tEnd + 0.28);

  // captions hold until just before the next one, up to half a second past their phrase
  CAPS.forEach(function (c, i) {
    var next = CAPS[i + 1] ? CAPS[i + 1][1] : D, end = Math.min(next - 0.12, c[2] + 0.45);
    tl.fromTo("#cp" + c[0], { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.16, ease: "power2.out" }, c[1] - 0.04);
    if (c[2] < D) tl.to("#cp" + c[0], { opacity: 0, duration: 0.12 }, end);
  });

  window.__timelines = window.__timelines || {};
  window.__timelines["main"] = tl;
})();
</script>
"""

head = ('<!doctype html>\n<html lang="ta">\n<head>\n<meta charset="UTF-8" />\n<meta name="viewport" content="width=1080, height=1920" />\n'
        '<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>\n<style>' + css + EXTRA_CSS + '</style>\n</head>\n<body>')
html = head + BODY.replace("__D__", str(D)) + SCRIPT.replace("__TIMING__", json.dumps(timing)) + "</body>\n</html>\n"

# ------------------------------------------------------------------ assets
for sub in ("assets/vo", "assets/sfx", "assets/fonts"):
    os.makedirs(os.path.join(DST, sub), exist_ok=True)
for f in os.listdir("shorts/ep02-v4/assets/fonts"):
    shutil.copy(os.path.join("shorts/ep02-v4/assets/fonts", f), os.path.join(DST, "assets/fonts", f))
for f in os.listdir("shorts/ep02-v4/assets/sfx-openverse"):      # CC0 effects from Openverse
    if f.endswith(".mp3"):
        shutil.copy(os.path.join("shorts/ep02-v4/assets/sfx-openverse", f), os.path.join(DST, "assets/sfx", f))
shutil.copy("shorts/ep02-v4/assets/sfx-openverse/CREDITS.md", os.path.join(DST, "assets/sfx/CREDITS.md"))
for f in ("hyperframes.json", "AGENTS.md", "CLAUDE.md"):
    shutil.copy(os.path.join("shorts/ep02-v4", f), os.path.join(DST, f))
open(os.path.join(DST, "package.json"), "w").write(open("shorts/ep02-v4/package.json").read().replace("ep02-v4", "ep03-v4"))
open(os.path.join(DST, "meta.json"), "w").write('{\n  "id": "ep03-v4",\n  "name": "ep03-v4",\n  "createdAt": "2026-11-13T21:00:00.000Z"\n}\n')
PHONE_EQ = "highpass=f=320,lowpass=f=3400,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,volume=1.5dB"
for ln in timing["lines"]:
    src, dst = f"voice/ep03_el/{ln['key']}.wav", os.path.join(DST, "assets/vo", ln["key"] + ".wav")
    if ln["key"] in ("open1", "open2", "open3"):                  # the call sounds like a phone line
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af", PHONE_EQ, "-ar", "48000", dst], check=True)
    else:
        shutil.copy(src, dst)
# stand-in ring (synthesized): two short bursts of a 400 Hz warble
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                "sine=f=400:d=0.8:r=44100,tremolo=f=25:d=0.9,volume='if(lt(t,0.34),1,if(lt(t,0.46),0,1))':eval=frame,afade=t=in:d=0.02,afade=t=out:st=0.76:d=0.04",
                "-codec:a", "libmp3lame", "-b:a", "128k", os.path.join(DST, "assets/sfx/ring.mp3")], check=True)

# ------------------------------------------------------------------ audio.json
L = {ln["key"]: ln for ln in timing["lines"]}
S = lambda k: L[k]["start"]
E = lambda k: L[k]["end"]
P = lambda k, i: L[k]["phrases"][i][0]
T = S("build") - 0.65
tWho, tAsk, tRw = S("who"), P("who", 3) - 0.08, S("rewind") - 0.12
tBoard, tRep, tSt = P("hook", 4) - 0.1, S("free"), S("stuck") - 0.12
tMiss, tNot, tAg = P("hook", 3) - 0.05, P("reveal", 1), P("reveal", 2)
tType, tC, tEnd = P("cta", 2) + 0.15, S("cta"), E("cta") - 0.05
LEN = {"click": 0.37, "click-soft": 0.37, "key-press": 0.4, "pop": 0.72, "whoosh": 0.57, "whoosh-short": 0.57, "whoosh-cinematic": 2.0,
       "impact-bass-1": 2.0, "impact-bass-2": 2.4, "notification": 1.5, "chime": 2.0, "sparkle": 1.0, "pen_short": 0.75, "stamp_real2": 0.55, "ring": 0.8}
cues = [
    (0.05, "ring", 0.35), (0.3, "pop", 0.2), (0.6, "pop", 0.2), (S("open1") - 0.1, "click", 0.4),
    (P("open2", 0) + 1.0, "pop", 0.25), (P("open2", 1) + 0.1, "pop", 0.25), (P("open3", 2), "pop", 0.25), (P("open3", 3), "notification", 0.3),
    (tWho, "whoosh-short", 0.3), (tAsk, "impact-bass-1", 0.45), (tRw, "whoosh", 0.4),
    (P("rewind", 2) - 0.25, "pop", 0.25), (P("rewind", 2) - 0.1, "pop", 0.25), (P("rewind", 2) + 0.05, "pop", 0.25), (P("rewind", 2) + 0.2, "pop", 0.25),
    (P("rewind", 3) - 0.05, "click", 0.4), (P("hook", 0), "pop", 0.25), (P("hook", 1), "pop", 0.25),
    (tMiss, "typing:0.8", 0.3), (tBoard - 0.1, "whoosh-short", 0.4), (tBoard + 0.15, "typing:1.0", 0.35), (tBoard + 1.0, "impact-bass-1", 0.5),
    (tSt - 0.1, "whoosh", 0.3), (tSt + 0.3, "pop", 0.2), (tSt + 0.6, "pop", 0.2), (tSt + 0.9, "pop", 0.2),
    (T, "impact-bass-2", 0.7), (T + 0.85, "whoosh-short", 0.25), (T + 1.4, "click", 0.45), (T + 1.7, "click", 0.45), (T + 2.0, "click", 0.45),
    (T + 2.95, "whoosh-cinematic", 0.35), (tNot + 0.15, "stamp_real2", 0.5), (tAg - 0.3, "pop", 0.3), (tAg + 0.1, "pop", 0.3), (tAg + 0.45, "pop", 0.3),
    (tRep - 0.15, "whoosh", 0.4), (tRep + 0.1, "pop", 0.3), (tRep + 0.8, "stamp_real2", 0.45), (tRep + 1.4, "stamp_real2", 0.45),
    (tRep + 2.5, "click", 0.35), (tRep + 3.1, "click", 0.35), (tRep + 3.4, "sparkle", 0.3),
    (S("twist") - 0.2, "whoosh", 0.35), (P("twist", 1) + 0.5, "pen_short", 0.35), (S("meta") - 0.18, "whoosh", 0.35),
    (P("meta", 1) + 1.5, "stamp_real2", 0.5), (S("human") - 0.18, "whoosh", 0.35),
    (S("human") + 0.3, "click", 0.35), (S("human") + 0.58, "click", 0.35), (S("human") + 0.86, "click", 0.35), (S("human") + 1.14, "click", 0.35),
    (P("human", 1) - 0.05, "chime", 0.4), (tC - 0.2, "whoosh", 0.35), (tC + 0.7, "pop", 0.3), (P("cta", 1) - 0.05, "pop", 0.25),
    (P("cta", 1) + 0.5, "click", 0.35), (P("cta", 2) - 0.25, "pop", 0.25),
    (tType, "key-press", 0.3), (tType + 0.1, "key-press", 0.3), (tType + 0.2, "key-press", 0.3), (tType + 0.3, "key-press", 0.3),
    (tType + 0.55, "click", 0.4), (tEnd + 0.05, "sparkle", 0.3),
]
fx = []
for start, name, vol in sorted(cues, key=lambda c: c[0]):
    if ":" in name:
        name, dur = name.split(":")[0], float(name.split(":")[1])
    else:
        dur = LEN[name]
    dur = min(dur, round(D - start - 0.02, 2))
    fx.append([round(start, 2), dur, name, vol])
json.dump({"vo": os.path.abspath("ep03/timing.json"), "fx": fx}, open("ep03/audio.json", "w"), indent=1)
open(os.path.join(DST, "index.html"), "w", encoding="utf-8").write(html)
print(f"wrote {DST}/index.html · {D} s · {len(fx)} effects")
