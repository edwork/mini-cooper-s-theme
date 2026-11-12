# Changelog

## 1.0.0 - 2026-11-11

First public release.

- Six colourways, each with light and dark modes: Island Blue ("Mini Cooper S"), British Racing Green, Chili Red,
  Midnight Black, Pepper White and Zesty Yellow.
- One self-contained theme file: the textures are SVGs embedded as data URIs, so HACS needs nothing in `www/`.
- `tools/build_theme.py` generates the theme; `--check` (run in CI) fails when the YAML is out of date.
- Redrawn S badge: a balanced S (the lower half is the upper turned 180°, with smooth joins), sized so its
  stroke ends and shadow are never clipped, with the highlight running down the middle of the stroke.
