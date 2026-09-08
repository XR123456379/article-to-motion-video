# Article to Motion Video

把文章转成中文动态讲解视频的 Codex Skill。默认 1920×1080、30fps、深绿底色与荧光绿强调，支持文字上浮、图形逐步出现、连接线动画、年轻男声和同步字幕。

这是由 AI 阅读文章、组织分镜，再调用脚本制作视频的工作流。脚本不包含通用网页爬虫，也不会单靠 URL 自动理解文章。

## 默认效果

- 男声：`zh-CN-YunxiNeural`，语速 `+10%`，音调 `-3Hz`。
- 配音先生成，字幕和场景使用真实语音时间；时长不锁定75秒。
- 字幕保留标点和英文名称，关键词绿色强调。
- 左上角署名默认“杰瑞”，`storyboard.brandText` 可修改或置空。
- 结尾收束内容，不播放大字品牌署名。

## 安装与使用

把本仓库放入你的 Codex skills 目录，文件夹命名为 `article-to-motion-video`，确保目录内直接包含 `SKILL.md`。准备 Python、Node.js/npm、FFmpeg/FFprobe，以及可运行的 HyperFrames 浏览器环境。

```powershell
python -m pip install -r requirements.txt
```

向 Codex 发送：

> 使用 $article-to-motion-video，把下面这篇文章做成动态讲解视频。沿用默认风格，输出MP4与源项目。

AI 需创建项目输入文件：`narration.txt`、`caption-plan.json` 和 `storyboard.json`。格式见 [字幕输入](references/caption-input.md) 和 [分镜格式](references/storyboard-schema.md)。

```powershell
python scripts/generate_voice.py path/to/project
python scripts/validate_storyboard.py path/to/project/storyboard.json
python scripts/build_composition.py path/to/project/storyboard.json path/to/project/index.html
cd path/to/project
npx.cmd hyperframes@0.8.31 check --snapshots
npx.cmd hyperframes@0.8.31 render . --quality high --output video.mp4 --workers 2
```

场景时长和字幕需要在配音之后根据生成的边界文件填入分镜。Windows 可用 `scripts/run_pipeline.cmd <project> <storyboard>` 合并校验、生成和lint。调整已有字幕时运行 `python scripts/align_captions.py <project>`，不必重新配音。

## 依赖与验证范围

已在 Windows、Python 3.12、Edge TTS 7.2.8、HyperFrames 0.8.31 的视频制作中验证基础效果。Mac/Linux 未做完整渲染验证；需准备中文字体，并将 `npx.cmd` 换成 `npx`。Edge TTS 使用在线服务，需要网络；HyperFrames 和字体的可用性取决于本地环境。

本包只包含 Skill 与脚本，不包含第三方文章、测试音视频、浏览器、字体、密钥或虚拟环境。HyperFrames、GSAP、Edge TTS 等依赖分别遵循其上游许可与服务条件。
