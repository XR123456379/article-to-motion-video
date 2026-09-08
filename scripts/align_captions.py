"""Align an explicit phrase plan to saved Edge TTS word boundaries, without another TTS call."""
import argparse
import json
import re
from pathlib import Path


def norm(text):
    return re.sub(r"[^\w]", "", text, flags=re.UNICODE)


def align(project):
    audio = project / "assets/audio"
    meta = json.loads((audio / "narration-boundaries.json").read_text(encoding="utf-8"))
    plan = json.loads((project / "caption-plan.json").read_text(encoding="utf-8"))
    paragraphs = [p.strip() for p in (project / "narration.txt").read_text(encoding="utf-8").split("\n\n") if p.strip()]
    if len(plan) != len(meta["segments"]) or len(plan) != len(paragraphs):
        raise ValueError("caption-plan must contain one phrase array per narration paragraph")
    cues, offset = [], 0.0
    for number, (pieces, duration, paragraph) in enumerate(zip(plan, meta["segments"], paragraphs), 1):
        words = json.loads((audio / f"segment-{number:02d}-boundaries.json").read_text(encoding="utf-8"))
        texts = [p if isinstance(p, str) else p["text"] for p in pieces]
        if norm("".join(texts)) != norm(paragraph):
            raise ValueError(f"paragraph {number}: phrases do not preserve narration")
        cursor, local = 0, []
        for piece, text in zip(pieces, texts):
            target, consumed, begin = norm(text), "", cursor
            if not target:
                raise ValueError("empty caption")
            while cursor < len(words) and len(consumed) < len(target):
                consumed += norm(words[cursor]["text"])
                cursor += 1
            if consumed != target:
                raise ValueError(f"paragraph {number}: phrase boundary splits a TTS token or text differs: {text}")
            start = offset + words[begin]["offset"] / 10_000_000
            end = offset + (words[cursor - 1]["offset"] + words[cursor - 1]["duration"]) / 10_000_000
            highlights = [] if isinstance(piece, str) else piece.get("highlight", [])
            if any(not word or word not in text for word in highlights):
                raise ValueError("highlight must occur in caption")
            cue = dict(start=round(start, 3), end=round(end, 3), text=text, highlight=highlights)
            if local and end - start < 0.8:
                local[-1]["end"] = cue["end"]
                local[-1]["text"] += text
                local[-1]["highlight"] += highlights
            else:
                local.append(cue)
        if cursor != len(words):
            raise ValueError(f"paragraph {number}: unmapped TTS tokens")
        cues.extend(local)
        offset += duration
    for i, cue in enumerate(cues):
        if cue["end"] <= cue["start"] or (i and cue["start"] < cues[i-1]["end"]):
            raise ValueError("invalid or overlapping cue times")
    (audio / "narration-cues.json").write_text(json.dumps(cues, ensure_ascii=False, indent=2), encoding="utf-8")
    def tc(value):
        ms = round(value * 1000)
        hours, ms = divmod(ms, 3600000)
        minutes, ms = divmod(ms, 60000)
        seconds, ms = divmod(ms, 1000)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{ms:03d}"
    (audio / "narration.srt").write_text("\n\n".join(f"{i}\n{tc(c['start'])} --> {tc(c['end'])}\n{c['text']}" for i, c in enumerate(cues, 1)) + "\n", encoding="utf-8")
    print(f"Aligned {len(cues)} captions from real TTS boundaries")
    return cues


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    align(parser.parse_args().project.resolve())
