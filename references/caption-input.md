# 配音与字幕输入

项目中准备 `narration.txt`：每个场景一个自然段，用空行分开。

`caption-plan.json` 是二维数组：外层与段落一一对应，内层按完整语义分短句，保留标点、英语空格及项目全名。例如：

```json
[
  [
    {"text":"用文字生成视频。", "highlight":["文字"]},
    {"text":"再让字幕跟随讲解。", "highlight":["字幕"]}
  ]
]
```

同一段所有字幕文字连接后必须等于口播（允许标点、空白差异，不能改字）。每条尽量1–4秒，长英文名称保持完整；只高亮关键词，不整句高亮。配音脚本需要网络、FFmpeg/FFprobe与edge-tts。它保存每段音频及原始WordBoundary；对齐脚本严格检查文字匹配并使用真实边界。切分落在一个TTS token中间时会报错，应调整短句，不要伪造时间。

默认男声 `zh-CN-YunxiNeural`，rate `+10%`，pitch `-3Hz`；可用 `--rate=+5%` 调慢。重新配音会覆盖该项目音频，应在新项目目录使用。已有音频调整字幕仅运行 align_captions.py。

`storyboard.subtitles` 从 `assets/audio/narration-cues.json` 读取，captionMode 为 `srt-phrase`。每段scene时长取 narration-boundaries.json 的 segments。beat.start 根据实际讲到该词的cue确定；同位置交接不要重叠，显示期间至少能完成入场动画。
