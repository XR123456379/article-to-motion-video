# Dark-grid design contract

Use a quiet editorial-tech look rather than a generic dashboard.

- Background: `#07110D`; foreground: `#F2F7F4`; accent: `#B7F34A`; muted text: `#B5C4BD`; line: `#385047`; panel: `#0E1D17`.
- Keep contrast high: foreground and accent on the background, with muted text only for secondary labels. Use thin 1px borders, a low-opacity grid, and a restrained accent glow.
- Reliable font stack: `"Microsoft YaHei UI", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif`; use `"Cascadia Mono", "Consolas", monospace` for tiny labels. Do not use HyperFrames-disabled fonts or rely on a remote font download.
- Headline: 60–86px, strong weight, short lines. Body and captions: 20–30px minimum. Use generous line-height and keep Chinese punctuation intact.
- Motion: 0.45–0.8s entrances, `power2.out` or `sine.out`, short connector draws after nodes, visible 24–44px text rises, and no perpetual loops. Stagger text and visual elements to follow the narration. A scene transition may be a 0.3–0.5s accent wipe or opacity handoff.
- Brand: persistent `杰瑞` at left 160px / top 40px in 32px accent type, above scene layers and clear of the scene kicker. No large outro signature or spoken brand sign-off; the ending retains only the small corner brand and the article conclusion.
- Rhythm: follow the faster narration specified in SKILL.md; shorten idle scene holds and introduce meaningful beats approximately every 2–3 seconds when supported by the speech. Keep text entrances smooth and captions readable. Rebuild timing from the new audio rather than applying visual-only playback speed.
- Avoid pure black, blue/purple gradients, noisy shaders, decorative 3D, excessive glow, and repeated identical card grids. Comparison panels should have meaningful labels; a flow should have a visible direction; split scenes should show a real contrast.
