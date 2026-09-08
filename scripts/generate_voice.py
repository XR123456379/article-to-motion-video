import asyncio
import argparse
import json
import re
import subprocess
from pathlib import Path

import edge_tts


parser = argparse.ArgumentParser(description="Generate Mandarin narration and real TTS word boundaries for a project.")
parser.add_argument("project", type=Path)
parser.add_argument("--rate", default="+10%")
args = parser.parse_args()
ROOT = args.project.resolve()
TEXT = ROOT / "narration.txt"
AUDIO_DIR = ROOT / "assets" / "audio"
VOICE = "zh-CN-YunxiNeural"
RATE = args.rate
PITCH = "-3Hz"


def ffprobe_duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        check=True, capture_output=True, text=True,
    )
    return float(result.stdout.strip())


async def synthesize(text: str, path: Path) -> list[dict]:
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH, boundary="WordBoundary")
    boundaries = []
    with path.open("wb") as output:
        async for item in communicate.stream():
            if item["type"] == "audio":
                output.write(item["data"])
            elif item["type"] == "WordBoundary":
                boundaries.append({"offset": item["offset"], "duration": item["duration"], "text": item["text"]})
    return boundaries


def srt_time(seconds: float) -> str:
    ms = max(0, round(seconds * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def make_cues(text: str, boundaries: list[dict], duration: float, offset: float) -> list[dict]:
    if not boundaries:
        raise RuntimeError("EdgeTTS returned no word timestamps")
    groups = []
    current = []
    char_count = 0
    for boundary in boundaries:
        current.append(boundary)
        char_count += len(boundary["text"])
        if char_count >= 12 or boundary["text"] in "。！？；，、":
            groups.append(current)
            current = []
            char_count = 0
    if current:
        groups.append(current)
    cues = []
    for group in groups:
        start = offset + group[0]["offset"] / 10_000_000
        end = offset + (group[-1]["offset"] + group[-1]["duration"]) / 10_000_000
        phrase = ""
        for item in group:
            token = item["text"]
            if phrase and token and phrase[-1].isascii() and token[0].isascii() and phrase[-1].isalnum() and token[0].isalnum():
                phrase += " "
            phrase += token
        english = re.findall(r"[A-Za-z][A-Za-z0-9/-]*", phrase)
        highlights = [english[0]] if english else ([phrase[:4]] if phrase else [])
        cues.append({"start": round(start, 3), "end": round(min(end, offset + duration), 3), "text": phrase, "highlight": highlights})
    return cues


async def main():
    paragraphs = [p.strip() for p in TEXT.read_text(encoding="utf-8").split("\n\n") if p.strip()]
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    segments = []
    all_cues = []
    timeline = 0.0
    for index, paragraph in enumerate(paragraphs, 1):
        segment_path = AUDIO_DIR / f"segment-{index:02d}.mp3"
        boundaries = await synthesize(paragraph, segment_path)
        duration = ffprobe_duration(segment_path)
        (AUDIO_DIR / f"segment-{index:02d}-boundaries.json").write_text(json.dumps(boundaries, ensure_ascii=False, indent=2), encoding="utf-8")
        segments.append(segment_path)
        timeline += duration
        print(f"segment {index}: {duration:.3f}s, {len(boundaries)} word boundaries")
    concat_file = AUDIO_DIR / "concat.txt"
    concat_file.write_text("\n".join(f"file '{p.as_posix().replace(chr(39), chr(39)+chr(92)+chr(39)+chr(39))}'" for p in segments) + "\n", encoding="utf-8")
    final_path = AUDIO_DIR / "narration.mp3"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c", "copy", str(final_path)], check=True)
    final_duration = ffprobe_duration(final_path)
    (AUDIO_DIR / "narration-boundaries.json").write_text(json.dumps({"voice": VOICE, "rate": RATE, "pitch": PITCH, "duration": final_duration, "segments": [ffprobe_duration(p) for p in segments]}, ensure_ascii=False, indent=2), encoding="utf-8")
    subprocess.run([__import__("sys").executable, str(Path(__file__).with_name("align_captions.py")), str(ROOT)], check=True)
    print(f"final: {final_duration:.3f}s; captions aligned from caption-plan.json")


if __name__ == "__main__":
    asyncio.run(main())
