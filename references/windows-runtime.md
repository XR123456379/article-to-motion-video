# Windows runtime notes

Run HyperFrames from the composition directory. When PowerShell blocks `npx.ps1`, use the executable shim without changing the machine execution policy:

```powershell
npx.cmd hyperframes doctor
npx.cmd hyperframes info
npx.cmd hyperframes tts --list
npx.cmd hyperframes lint
npx.cmd hyperframes check --snapshots
npx.cmd hyperframes render -o outputs\draft.mp4
```

For the Skill's local build step, use `scripts\run_pipeline.cmd <project> <storyboard.json>`. The wrapper applies `ExecutionPolicy Bypass` only to its child PowerShell process; it does not change the machine or user execution policy.

Record the results of `doctor`: Node, FFmpeg/FFprobe, Chrome Headless Shell, whisper-cpp, and Kokoro TTS are separate capabilities. The absence of whisper-cpp or Kokoro means captions/audio may need another declared provider; it does not justify fabricating timestamps or voice IDs. `hyperframes browser ensure` can install the local Chrome headless dependency when permitted. Do not alter plugin caches; keep generated projects and outputs in the user's requested workspace.
