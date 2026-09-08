#!/usr/bin/env python3
"""Build a deterministic, beat-driven HyperFrames HTML composition."""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def attrs(cid: str, start: float, duration: float, track: int) -> str:
    return f'id="{esc(cid)}" data-start="{start:g}" data-duration="{duration:g}" data-track-index="{track}"'


def highlight_markup(text: str, highlights: list[str]) -> str:
    if not highlights:
        return esc(text)
    pieces: list[str] = []
    remaining = text
    while remaining:
        hits = [(remaining.find(word), word) for word in highlights if word and remaining.find(word) >= 0]
        if not hits:
            pieces.append(esc(remaining))
            break
        pos, word = min(hits, key=lambda item: item[0])
        if pos:
            pieces.append(esc(remaining[:pos]))
        pieces.append(f'<span class="caption-highlight">{esc(word)}</span>')
        remaining = remaining[pos + len(word):]
    return "".join(pieces)


def visual_markup(sid: str, kind: str, visual_labels: list[str]) -> tuple[str, list[str], list[str]]:
    """Return visual HTML, node ids, and connector ids for choreography."""
    node_ids: list[str] = []
    link_ids: list[str] = []
    if kind == "cover":
        node_ids = [f"{sid}-mark-{i}" for i in range(1, 4)]
        labels = [esc(x) for x in visual_labels]
        visual = '<div id="%s-visual" class="cover-mark" data-track-index="2">%s</div>' % (sid, "".join(f'<span id="{nid}"><b>{label}</b></span>' for nid, label in zip(node_ids, labels)))
    elif kind == "comparison":
        node_ids = [f"{sid}-card-{i}" for i in range(1, 4)]
        labels = [esc(x) for x in visual_labels]
        visual = f'<div id="{sid}-visual" class="compare-lines" data-track-index="2">' + ''.join(f'<i id="{nid}"><b>{label}</b></i>' for nid, label in zip(node_ids, labels)) + '</div>'
    elif kind == "flow":
        node_ids = [f"{sid}-node-{i}" for i in range(1, 4)]
        link_ids = [f"{sid}-link-{i}" for i in range(1, 3)]
        labels = [esc(x) for x in visual_labels]
        visual = f'<div id="{sid}-visual" class="flow-lines" data-track-index="2">' + ''.join(f'<i id="{nid}"><b>{label}</b></i>' for nid, label in zip(node_ids, labels)) + ''.join(f'<b id="{lid}" class="visual-link"></b>' for lid in link_ids) + '</div>'
    elif kind == "split":
        node_ids = [f"{sid}-panel-{i}" for i in range(1, 3)]
        labels = [esc(x) for x in visual_labels]
        visual = f'<div id="{sid}-visual" class="split-lines" data-track-index="2">' + ''.join(f'<i id="{nid}"><b>{label}</b></i>' for nid, label in zip(node_ids, labels)) + '</div>'
    elif kind == "summary":
        node_ids = [f"{sid}-card-{i}" for i in range(1, 5)]
        link_ids = [f"{sid}-link-{i}" for i in range(1, 3)]
        labels = [esc(x) for x in visual_labels]
        visual = f'<div id="{sid}-visual" class="summary-lines" data-track-index="2">' + ''.join(f'<i id="{nid}"><b>{label}</b></i>' for nid, label in zip(node_ids, labels)) + ''.join(f'<b id="{lid}" class="visual-link"></b>' for lid in link_ids) + '</div>'
    else:
        visual = ""
    return visual, node_ids, link_ids


def scene_markup(scene: dict, index: int) -> tuple[str, list[str]]:
    sid = scene["id"]
    start, duration = float(scene["start"]), float(scene["duration"])
    common = f'data-start="{start:g}" data-duration="{duration:g}"'
    count = {"cover": 3, "comparison": 3, "flow": 3, "split": 2, "summary": 4, "outro": 0}[scene["type"]]
    labels = scene.get("visualLabels", [""] * count)
    if len(labels) != count:
        raise ValueError(f"{sid}: visualLabels needs {count} labels")
    visual, node_ids, link_ids = visual_markup(sid, scene["type"], labels)
    beat_markup = []
    for i, beat in enumerate(scene.get("beats", []), 1):
        bid = f"{sid}-beat-{i}"
        beat_class = " beat-item beat-accent" if beat.get("accent") else " beat-item"
        beat_markup.append(f'<div id="{bid}" style="top:{(i - 1) * 82}px" class="clip{beat_class}" data-start="{float(beat["start"]):g}" data-duration="{float(beat.get("duration", 1.2)):g}" data-track-index="6">{esc(beat["text"])}</div>')
    markup = f'''<section {attrs(sid, start, duration, 1)} class="clip scene scene-{esc(scene["type"])}">
  <div {attrs(f"{sid}-kicker", start, duration, 3)} class="clip scene-kicker">{esc(scene["type"].upper())} · {index + 1:02d}</div>
  <h1 {attrs(f"{sid}-headline", start, duration, 4)} class="clip">{esc(scene["headline"])}</h1>
  <p {attrs(f"{sid}-body", start, duration, 5)} class="clip">{esc(scene["body"])}</p>
  <div {attrs(f"{sid}-accent", start, duration, 7)} class="clip scene-accent">{esc(scene["accent"])}</div>
  <div id="{sid}-beats" class="beat-stack">{"".join(beat_markup)}</div>
  {visual}
</section>'''
    anims: list[str] = []
    anims += [f'fromTo("#{sid}", {{opacity:0,y:12}}, {{opacity:1,y:0,duration:0.45,ease:"power2.out",immediateRender:false}}, {start:g});']
    anims += [f'fromTo("#{sid}-kicker", {{opacity:0,y:26}}, {{opacity:1,y:0,duration:0.45,ease:"power2.out",immediateRender:false}}, {start + 0.10:g});']
    anims += [f'fromTo("#{sid}-headline", {{opacity:0,y:42}}, {{opacity:1,y:0,duration:0.62,ease:"power3.out",immediateRender:false}}, {start + 0.35:g});']
    anims += [f'fromTo("#{sid}-body", {{opacity:0,y:34}}, {{opacity:1,y:0,duration:0.58,ease:"power2.out",immediateRender:false}}, {start + 0.68:g});']
    anims += [f'fromTo("#{sid}-accent", {{opacity:0,y:24}}, {{opacity:1,y:0,duration:0.5,ease:"power2.out",immediateRender:false}}, {start + 1.0:g});']
    for i, beat in enumerate(scene.get("beats", []), 1):
        at = float(beat["start"])
        anims.append(f'fromTo("#{sid}-beat-{i}", {{opacity:0,y:44}}, {{opacity:1,y:0,duration:0.55,ease:"power3.out",immediateRender:false}}, {at:g});')
        if beat.get("accent"):
            anims.append(f'to("#{sid}-beat-{i}", {{scale:1.025,duration:0.18,yoyo:true,repeat:1,ease:"sine.inOut"}}, {at + 0.58:g});')
    for i, nid in enumerate(node_ids):
        at = start + 0.9 + i * 0.62
        anims.append(f'fromTo("#{nid}", {{opacity:0,scale:0.72,y:24}}, {{opacity:1,scale:1,y:0,duration:0.48,ease:"back.out(1.35)",immediateRender:false}}, {at:g});')
    for i, lid in enumerate(link_ids):
        at = start + 2.15 + i * 0.8
        anims.append(f'fromTo("#{lid}", {{opacity:1,scaleX:0}}, {{opacity:1,scaleX:1,duration:0.38,ease:"power2.out",immediateRender:false}}, {at:g});')
    return markup, anims


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("storyboard", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    data = json.loads(args.storyboard.read_text(encoding="utf-8"))
    blocks: list[str] = []
    timeline: list[str] = ["window.__timelines = window.__timelines || {};", "const tl = gsap.timeline({ paused: true });", "const fromTo = (s, a, b, at) => tl.fromTo(s, a, b, at);", "const to = (s, vars, at) => tl.to(s, vars, at);"]
    for index, scene in enumerate(data["scenes"]):
        block, anims = scene_markup(scene, index)
        blocks.append(block)
        timeline.extend(anims)
    for scene in data["scenes"][:-1]:
        at = float(scene["start"]) + float(scene["duration"]) - 0.38
        tid = f'{scene["id"]}-transition'
        timeline.append(f'fromTo("#{tid}", {{scaleX:0}}, {{scaleX:1,duration:0.34,ease:"power2.out",immediateRender:false}}, {at:g});')
    subtitle_markup: list[str] = []
    for i, sub in enumerate(data.get("subtitles", []), 1):
        start, end = float(sub["start"]), float(sub["end"])
        sid = f"subtitle-{i:02d}"
        subtitle_markup.append(f'<div id="{sid}" class="clip caption-rail" data-start="{start:g}" data-duration="{end-start:g}" data-track-index="20">{highlight_markup(sub["text"], sub.get("highlight", []))}</div>')
        timeline.append(f'fromTo("#{sid}", {{opacity:0,y:30}}, {{opacity:1,y:0,duration:0.28,ease:"power2.out",immediateRender:false}}, {start:g});')
        if sub.get("highlight"):
            timeline.append(f'fromTo("#{sid} .caption-highlight", {{scale:0.92,textShadow:"0 0 0 rgba(183,243,74,0)"}}, {{scale:1.06,textShadow:"0 0 22px rgba(183,243,74,.48)",duration:0.32,ease:"back.out(1.35)",stagger:0.06,immediateRender:false}}, {start + 0.18:g});')
            timeline.append(f'to("#{sid} .caption-highlight", {{scale:1,textShadow:"0 0 12px rgba(183,243,74,.25)",duration:0.22,ease:"sine.out"}}, {start + 0.52:g});')
        timeline.append(f'to("#{sid}", {{opacity:0,duration:0.16,ease:"power1.in"}}, {max(start, end - 0.16):g});')
    timeline.append('window.__timelines["main"] = tl;')
    transitions = "".join(f'<div id="{esc(scene["id"])}-transition" class="clip scene-transition" data-start="{float(scene["start"])+float(scene["duration"])-0.38:g}" data-duration="0.38" data-track-index="8"></div>' for scene in data["scenes"][:-1])
    audio = data.get("audio")
    audio_markup = ""
    if audio:
        audio_markup = f'<audio id="narration-audio" src="{esc(audio["path"])}" data-start="{float(audio.get("start", 0)):g}" data-duration="{float(audio["duration"]):g}" data-track-index="10" data-volume="{float(audio.get("volume", 1)):g}"></audio>'
    brand_markup = f'<div {attrs("brand-label", 0, float(data["duration"]), 30)} class="clip brand-label">{esc(data.get("brandText", "杰瑞"))}</div>'
    css = '''
    @font-face { font-family:"Microsoft YaHei UI"; src:local("Microsoft YaHei UI"); }
    @font-face { font-family:"Cascadia Mono"; src:local("Cascadia Mono"); }
    :root { --bg:#07110D; --fg:#F2F7F4; --accent:#B7F34A; --muted:#B5C4BD; --line:#385047; --panel:#0E1D17; }
    * { box-sizing:border-box; } html,body { margin:0; width:1920px; height:1080px; overflow:hidden; background:var(--bg); color:var(--fg); font-family:"Microsoft YaHei UI",sans-serif; }
    body::before { content:""; position:fixed; inset:0; opacity:.19; background-image:linear-gradient(var(--line) 1px,transparent 1px),linear-gradient(90deg,var(--line) 1px,transparent 1px); background-size:64px 64px; pointer-events:none; }
    #root { position:relative; width:1920px; height:1080px; background:radial-gradient(circle at 78% 22%,rgba(183,243,74,.08),transparent 34%),var(--bg); }
    .scene { position:absolute; inset:0; padding:150px 160px; border:1px solid rgba(56,80,71,.35); background:rgba(7,17,13,.84); }
    .scene-kicker { position:absolute; top:106px; left:160px; color:var(--accent); font:700 22px/1 "Cascadia Mono",monospace; letter-spacing:2px; opacity:0; }
    .brand-label { position:absolute; left:160px; top:40px; z-index:30; color:var(--accent); font-size:32px; line-height:1; font-weight:800; letter-spacing:2px; }
    h1 { position:absolute; top:208px; left:160px; width:1260px; margin:0; font-size:78px; line-height:1.13; letter-spacing:-2px; opacity:0; }
    p { position:absolute; top:410px; left:164px; width:920px; margin:0; color:var(--muted); font-size:30px; line-height:1.55; opacity:0; }
    .scene-accent { position:absolute; top:820px; left:164px; color:var(--accent); font-size:26px; font-weight:700; opacity:0; }
    .beat-stack { position:absolute; left:164px; top:480px; width:960px; height:380px; }
    .beat-item { position:absolute; left:0; top:0; max-width:960px; overflow-wrap:anywhere; padding:11px 20px; border-left:4px solid var(--line); background:rgba(14,29,23,.92); color:var(--fg); font-size:32px; font-weight:700; opacity:0; }
    .beat-accent { border-left-color:var(--accent); color:var(--accent); }
    .caption-rail { position:absolute; left:160px; right:160px; bottom:80px; min-height:64px; padding:12px 22px; border-left:4px solid var(--accent); background:rgba(14,29,23,.95); color:#fff; font-size:38px; line-height:1.25; opacity:0; }
    .caption-highlight { display:inline-block; color:var(--accent); text-shadow:0 0 15px rgba(183,243,74,.28); font-weight:800; }
    .cover-mark,.compare-lines,.flow-lines,.split-lines,.summary-lines { position:absolute; right:210px; top:248px; width:380px; height:330px; }
    .cover-mark span { display:flex; align-items:center; justify-content:center; width:180px; height:58px; margin:28px 0; border:2px solid var(--accent); box-shadow:0 0 22px rgba(183,243,74,.32); clip-path:polygon(12% 0,100% 0,88% 100%,0 100%); opacity:0; }
    .cover-mark b,.compare-lines b,.flow-lines b,.split-lines b,.summary-lines i b { display:block; color:var(--fg); font:700 20px/1.15 "Microsoft YaHei UI",sans-serif; text-align:center; padding:0 8px; }
    .cover-mark span:nth-child(2) { margin-left:90px; background:var(--accent); }
    .compare-lines i,.flow-lines i,.split-lines i,.summary-lines i { display:flex; align-items:center; justify-content:center; position:absolute; border:2px solid var(--accent); background:var(--panel); opacity:0; }
    .compare-lines i { width:155px; height:155px; top:20px; } .compare-lines i:nth-child(2) { left:205px; border-color:var(--fg); } .compare-lines i:nth-child(3) { top:210px; left:104px; width:170px; height:88px; border-color:var(--line); }
    .flow-lines i { width:112px; height:112px; border-radius:50%; top:105px; } .flow-lines i:nth-child(2) { left:135px; } .flow-lines i:nth-child(3) { left:270px; }
    .visual-link { display:block; position:absolute; top:160px; width:66px; height:3px; opacity:0; transform-origin:left center; background:var(--accent); z-index:0; } .compare-lines i,.flow-lines i,.split-lines i,.summary-lines i { z-index:1; } .flow-lines .visual-link:nth-of-type(1) { left:112px; } .flow-lines .visual-link:nth-of-type(2) { left:247px; }
    .split-lines i { width:170px; height:250px; top:40px; } .split-lines i:nth-child(2) { left:210px; border-color:var(--fg); }
    .summary-lines i { width:140px; height:90px; top:20px; } .summary-lines i:nth-child(2) { left:170px; } .summary-lines i:nth-child(3) { top:140px; } .summary-lines i:nth-child(4) { top:140px; left:170px; border-color:var(--fg); }
    .summary-lines .visual-link { left:140px; top:64px; } .summary-lines .visual-link:nth-of-type(2) { left:140px; top:184px; } .cover-mark span:nth-child(2) b { color:var(--bg); }
    .scene-summary h1 { width:1080px; }
    .scene-transition { position:absolute; left:160px; right:160px; bottom:166px; height:2px; background:var(--accent); transform-origin:left center; opacity:.7; }
    '''
    html_doc = f'''<!doctype html><html lang="zh-CN"><head><meta charset="UTF-8" /><meta name="viewport" content="width=1920, height=1080" /><title>{esc(data["title"])}</title><script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script><style>{css}</style></head><body><div id="root" data-composition-id="main" data-start="0" data-duration="{float(data["duration"]):g}" data-width="{int(data["width"])}" data-height="{int(data["height"])}" data-fps="{int(data["fps"])}">{"".join(blocks)}{transitions}{"".join(subtitle_markup)}{audio_markup}{brand_markup}</div><script>{"".join(timeline)}</script></body></html>'''
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html_doc, encoding="utf-8", newline="\n")
    print(f"Wrote {args.output} ({len(html_doc)} bytes; {len(data.get('subtitles', []))} subtitles)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
