#!/usr/bin/env python3
"""Deterministically validate an article-to-motion-video storyboard."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

SCENE_TYPES = ("cover", "comparison", "flow", "split", "summary", "outro")


def fail(errors: list[str]) -> int:
    for item in errors:
        print(f"ERROR: {item}")
    return 1


def main() -> int:
    if len(sys.argv) != 2:
        return fail(["usage: validate_storyboard.py STORYBOARD.json"])
    path = Path(sys.argv[1])
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return fail([f"cannot read JSON: {exc}"])
    errors: list[str] = []
    if not isinstance(data, dict):
        return fail(["root must be an object"])
    for key in ("title", "source", "duration", "fps", "width", "height", "voice", "captionMode", "scenes", "subtitles"):
        if key not in data:
            errors.append(f"missing root field: {key}")
    root_duration = data.get("duration")
    valid_root_duration = not (
        not isinstance(root_duration, (int, float))
        or isinstance(root_duration, bool)
        or not math.isfinite(float(root_duration))
        or root_duration <= 0
    )
    if not valid_root_duration:
        errors.append("duration must be a finite positive number")
    if data.get("fps") != 30 or data.get("width") != 1920 or data.get("height") != 1080:
        errors.append("canvas must be 1920x1080 at 30fps")
    if data.get("captionMode") not in ("word-timestamps", "srt-phrase", "scene-phrase-degraded"):
        errors.append("captionMode must be word-timestamps, srt-phrase, or scene-phrase-degraded")
    voice = data.get("voice")
    if not isinstance(voice, dict) or voice.get("status") not in ("unavailable", "generated"):
        errors.append("voice.status must be unavailable or generated")
    scenes = data.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        return fail(errors + ["scenes must be a non-empty array"])
    ids: set[str] = set()
    starts = 0.0
    seen_types: list[str] = []
    for index, scene in enumerate(scenes):
        if not isinstance(scene, dict):
            errors.append(f"scene {index} must be an object")
            continue
        for key in ("id", "type", "start", "duration", "headline", "body", "accent", "beats"):
            if key not in scene:
                errors.append(f"scene {index} missing field: {key}")
        sid = scene.get("id")
        if not isinstance(sid, str) or not sid:
            errors.append(f"scene {index} id must be a non-empty string")
        elif sid in ids:
            errors.append(f"duplicate scene id: {sid}")
        else:
            ids.add(sid)
        stype = scene.get("type")
        seen_types.append(stype)
        if stype not in SCENE_TYPES:
            errors.append(f"scene {index} type must be one of {SCENE_TYPES}")
        start, duration = scene.get("start"), scene.get("duration")
        if not isinstance(start, (int, float)) or not isinstance(duration, (int, float)) or duration <= 0:
            errors.append(f"scene {index} start/duration must be positive numbers")
        else:
            if abs(float(start) - starts) > 1e-6:
                errors.append(f"scene {index} starts at {start}, expected contiguous {starts:g}")
            starts += float(duration)
        if not isinstance(scene.get("headline"), str) or not scene.get("headline", "").strip():
            errors.append(f"scene {index} headline must be non-empty text")
        if not isinstance(scene.get("body"), str) or not scene.get("body", "").strip():
            errors.append(f"scene {index} body must be non-empty text")
        if not isinstance(scene.get("accent"), str) or not scene.get("accent", "").strip():
            errors.append(f"scene {index} accent must be non-empty text")
        beats = scene.get("beats")
        if not isinstance(beats, list) or len(beats) < 3:
            errors.append(f"scene {index} beats must contain at least 3 items")
        elif any(not isinstance(b, dict) for b in beats):
            errors.append(f"scene {index} beats must contain objects")
        else:
            scene_start, scene_end = float(scene.get("start", 0)), float(scene.get("start", 0)) + float(scene.get("duration", 0))
            for bi, beat in enumerate(beats):
                for key in ("text", "start", "kind"):
                    if key not in beat:
                        errors.append(f"scene {index} beat {bi} missing field: {key}")
                if not isinstance(beat.get("text"), str) or not beat.get("text", "").strip():
                    errors.append(f"scene {index} beat {bi} text must be non-empty")
                if not isinstance(beat.get("start"), (int, float)) or not scene_start <= float(beat.get("start", -1)) < scene_end:
                    errors.append(f"scene {index} beat {bi} start must be inside scene")
    subtitles = data.get("subtitles")
    audio = data.get("audio")
    narration_duration = float(root_duration) if valid_root_duration else None
    if narration_duration is not None and isinstance(audio, dict) and isinstance(audio.get("duration"), (int, float)):
        if not isinstance(audio.get("duration"), bool) and math.isfinite(float(audio["duration"])) and audio["duration"] > 0:
            narration_duration = min(float(root_duration), float(audio["duration"]))
    if not isinstance(subtitles, list) or not subtitles:
        errors.append("subtitles must be a non-empty array")
    else:
        previous_end = -1.0
        for index, sub in enumerate(subtitles):
            if not isinstance(sub, dict) or not all(key in sub for key in ("start", "end", "text", "highlight")):
                errors.append(f"subtitle {index} must contain start, end, text, highlight")
                continue
            start, end = sub.get("start"), sub.get("end")
            if not isinstance(start, (int, float)) or not isinstance(end, (int, float)) or end <= start:
                errors.append(f"subtitle {index} start/end must be increasing numbers")
            elif start < 0 or (narration_duration is not None and end > narration_duration + 1e-6):
                errors.append(f"subtitle {index} must stay within narration 0..{narration_duration:g}s")
            if isinstance(start, (int, float)) and start < previous_end - 1e-6:
                errors.append(f"subtitle {index} overlaps subtitle {index - 1}")
            if isinstance(end, (int, float)):
                previous_end = float(end)
            if not isinstance(sub.get("text"), str) or not sub.get("text", "").strip():
                errors.append(f"subtitle {index} text must be non-empty")
            if not isinstance(sub.get("highlight"), list) or any(not isinstance(x, str) for x in sub.get("highlight", [])):
                errors.append(f"subtitle {index} highlight must be a string array")
        if subtitles and isinstance(subtitles[0], dict) and float(subtitles[0].get("start", -1)) > 0.1 + 1e-6:
            errors.append("subtitles must start at or before 0.1s")
    if seen_types != list(SCENE_TYPES):
        errors.append(f"scene types/order must be exactly {list(SCENE_TYPES)}")
    if valid_root_duration and abs(starts - float(root_duration)) > 1e-6:
        errors.append(f"scene durations sum to {starts:g}, expected {data.get('duration')}")
    if errors:
        return fail(errors)
    print(f"OK: {path} | {len(scenes)} scenes | {data['duration']}s | {data['width']}x{data['height']} @ {data['fps']}fps")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
