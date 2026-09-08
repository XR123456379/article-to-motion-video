# Storyboard schema

`storyboard.json` is the source of truth for timing and on-screen wording. It is intentionally small so a reviewer can compare every claim with the article.

Optional root `brandText` defaults to `杰瑞`; use an empty string to hide it. Each scene should supply `visualLabels`: cover/comparison/flow need 3 short labels, split needs 2, summary needs 4, outro needs 0. Labels must come from the current article; omitted labels produce empty shapes for backward compatibility. Use 3–4 short beats per scene with the fixed row layout and inspect line wrapping. Voice timing inputs are described in [caption-input.md](caption-input.md).

```json
{
  "title": "string",
  "source": "string",
  "duration": 75,
  "fps": 30,
  "width": 1920,
  "height": 1080,
  "voice": {"status": "unavailable|generated", "id": null, "language": "zh", "gender": "male|female|unknown", "rate": "+10%"},
  "captionMode": "word-timestamps|srt-phrase|scene-phrase-degraded",
  "scenes": [
    {"id": "cover-01", "type": "cover", "start": 0, "duration": 6, "headline": "string", "body": "string", "accent": "string", "beats": [{"text": "short phrase", "start": 0.5, "duration": 1.5, "kind": "node", "accent": true}]}
  ],
  "subtitles": [{"start": 0.1, "end": 2.8, "text": "string", "highlight": ["keyword"]}]
}
```

Required scene order for the compact article explainer is `cover`, `comparison`, `flow`, `split`, `summary`, `outro`. Starts must be contiguous and durations must sum exactly to `duration`. Every scene needs at least three `beats`; beat starts are absolute composition seconds and must fall within the scene. Headline text must be at least 60px and body/caption text at least 20px in the generated composition. `accent`, headline, body, beats, and subtitles must be supported by the article; do not add factual claims in the storyboard.

`subtitles` are the only narration-synchronised caption source. They must be monotonic, non-overlapping, cover the real narration window, and carry a `highlight` array for the active keyword treatment. The builder turns each subtitle into an independently timed `.clip`; it does not display the legacy scene caption rail.

The persistent top-left `杰瑞` brand is generated separately from scene content. `outro` means a closing takeaway, not a brand card. Do not put a brand sign-off in its headline, body, accent, beats, narration, or subtitles. Cue counts and overall duration must follow the new article and generated narration, not the previous example.

The example's 75 seconds is illustrative, not a required runtime. Use a positive finite duration based on the faster narration and a 0.4–0.8 second closing hold. Record the actual provider-specific rate in `voice.rate`; the personal Edge TTS default is `+10%`. Derive all scene, beat, and subtitle timings from that audio.

The validator is deterministic and dependency-free:

```powershell
python scripts/validate_storyboard.py path\to\storyboard.json
```
