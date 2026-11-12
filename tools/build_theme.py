#!/usr/bin/env python3
"""Mini Cooper S theme for Home Assistant, after a 2022 MINI Cooper S in Island Blue with the Multitone roof.

The car's details, and where each one goes:
  - Island Blue metallic body       -> the page: a metallic blue sheen with flake
  - Multitone (ombre) roof          -> the band under the header, and the strip along each card's top edge:
                                       bright San Marino blue at the windshield, through deep blue, to Jet Black
  - Black bonnet stripes, white pin -> two fixed stripes down the page, like looking over the bonnet
  - Chili Red "S" grille badge      -> the primary/active color, and a chrome-edged S badge at the page's bottom right
  - Jet Black roof / piano trim     -> the header, sidebar and (dark mode) cards
  - Round LED halo headlights       -> rounder cards (20 px)

Theme "Mini Cooper S": light (pale Island Blue, pearl cards) and dark (Island Blue at night, piano black cards).

The flake textures and the S badge are SVGs embedded as data URIs, so the theme is a single self-contained YAML
file (HACS installs only the themes/ folder; there's nothing to copy into www/).

  python3 tools/build_theme.py            # regenerate themes/mini_cooper_s.yaml
  python3 tools/build_theme.py --check    # exit 1 if themes/mini_cooper_s.yaml is out of date (CI)

Then reload themes in Home Assistant (Developer tools > Actions > frontend.reload_themes). Edit this script, not
the generated file. Standard library only, Python 3.9+.
"""
import base64
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
THEME = REPO / "themes" / "mini_cooper_s.yaml"

ISLAND = "#2f6690"          # Island Blue, mid tone
ISLAND_HI = "#4d86b3"       # sun on the bonnet
ISLAND_LO = "#173650"       # shadowed flank
ROOF = ["#3d8fe3", "#2b62b8", "#1d2f63", "#11152a", "#0a0a0d"]   # windshield -> spoiler
STRIPE = "#16181c"          # bonnet stripe
PIN = "#eef2f6"             # white pinstripe
CHILI = "#d72631"           # S badge
CHILI_DARK = "#e23a44"      # S badge, lifted for dark backgrounds
CHROME = ["#f4f6f8", "#a9b0b8", "#e3e7eb", "#7d858e"]
JET = "#0b0c0f"


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def hexc(c):
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(v))) for v in c)


def mix(a, b, t):
    ra, rb = rgb(a), rgb(b)
    return hexc([ra[i] + (rb[i] - ra[i]) * t for i in range(3)])


def rgbs(h):
    return ", ".join(str(v) for v in rgb(h))


def roof_gradient(angle="90deg"):
    stops = ", ".join(f"{c} {round(i * 100 / (len(ROOF) - 1))}%" for i, c in enumerate(ROOF))
    return f"linear-gradient({angle}, {stops})"


# ---- SVG assets ----------------------------------------------------------------------------------------------------
def flake_svg(alpha_gain, alpha_bias, size=180):
    """Metallic flake: sparse bright points (thresholded turbulence) over a faint fine grain."""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
            '<filter id="f" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">'
            '<feTurbulence type="fractalNoise" baseFrequency="2.2" numOctaves="2" seed="3" stitchTiles="stitch"/>'
            f'<feColorMatrix type="matrix" values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 {alpha_gain} 0 0 0 {alpha_bias}"/></filter>'
            '<filter id="g" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">'
            '<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="17" stitchTiles="stitch"/>'
            '<feColorMatrix type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.25 0 0 0 -0.09"/></filter>'
            f'<rect width="{size}" height="{size}" filter="url(#g)"/>'
            f'<rect width="{size}" height="{size}" filter="url(#f)"/></svg>')


# The S spine, drawn upright in a 100 x 120 box centred on (50, 60). The first half runs from the top terminal to
# the centre; the second half is the first turned 180 degrees about the centre, so the bowls match exactly and every
# join is smooth (each joint's two control points are collinear with it).
S_CENTRE = (50.0, 60.0)
S_FIRST_HALF = [                       # cubic segments: (control 1, control 2, end); starts at S_START
    ((76, 12), (59, 9.125), (47, 9.5)),  # top terminal curling up and over
    ((31, 10), (19, 20), (19, 33)),      # top of the upper bowl, down the left side
    ((19, 47), (33, 53), (50, 60)),      # into the spine, through the centre
]
S_START = (81, 22)
S_SKEW = 14                            # italic lean, degrees
S_CHROME_W, S_EDGE_W, S_RED_W, S_SHINE_W = 21, 16.6, 15, 3


def s_segments():
    turn = lambda p: (2 * S_CENTRE[0] - p[0], 2 * S_CENTRE[1] - p[1])
    pts = [S_START] + [p for seg in S_FIRST_HALF for p in seg]           # P0 C C P1 C C P2 C C P3(centre)
    second = [turn(p) for p in reversed(pts[:-1])]                       # centre -> ... -> turned start
    pts += second
    return pts[0], [tuple(pts[i:i + 3]) for i in range(1, len(pts), 3)]


def s_path():
    start, segs = s_segments()
    return f"M{start[0]:g} {start[1]:g}" + "".join(
        "C" + " ".join(f"{x:g} {y:g}" for x, y in seg) for seg in segs)


def s_bounds(pad):
    """Bounding box of the skewed spine (sampled), grown by pad on every side."""
    start, segs = s_segments()
    k = math.tan(math.radians(S_SKEW))
    xs, ys, p0 = [], [], start
    for c1, c2, p3 in segs:
        for i in range(41):
            t = i / 40
            u = 1 - t
            x = u ** 3 * p0[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t ** 3 * p3[0]
            y = u ** 3 * p0[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t ** 3 * p3[1]
            xs.append(x - k * (y - S_CENTRE[1]))
            ys.append(y)
        p0 = p3
    return min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad


def s_badge_svg():
    """The grille's Chili Red S: italic, chrome-edged, a dark seam between chrome and red, and a soft highlight
    down the middle of the stroke. The canvas and the shadow's filter region are sized from the shape itself, so
    nothing (stroke ends, round caps, shadow) is clipped."""
    shadow_dy, shadow_blur = 2.5, 2
    x0, y0, x1, y1 = s_bounds(S_CHROME_W / 2 + shadow_dy + 3 * shadow_blur)
    w, h = x1 - x0, y1 - y0
    vb = f"{x0:.1f} {y0:.1f} {w:.1f} {h:.1f}"
    grad = f'x1="0" y1="{y0:.1f}" x2="0" y2="{y1:.1f}" gradientUnits="userSpaceOnUse"'
    chrome = "".join(f'<stop offset="{i / (len(CHROME) - 1):.2f}" stop-color="{c}"/>' for i, c in enumerate(CHROME))
    path = s_path()
    cx, cy = S_CENTRE
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w / 2:.0f}" height="{h / 2:.0f}" viewBox="{vb}">'
            f'<defs><linearGradient id="c" {grad}>{chrome}</linearGradient>'
            f'<linearGradient id="r" {grad}><stop offset="0" stop-color="{mix(CHILI, "#ffffff", 0.22)}"/>'
            f'<stop offset=".5" stop-color="{CHILI}"/><stop offset="1" stop-color="{mix(CHILI, "#000000", 0.32)}"/></linearGradient>'
            f'<filter id="d" filterUnits="userSpaceOnUse" x="{x0:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{h:.1f}">'
            f'<feDropShadow dx="0" dy="{shadow_dy}" stdDeviation="{shadow_blur}" flood-color="#000" flood-opacity=".45"/></filter>'
            f'<path id="s" d="{path}"/></defs>'
            f'<g transform="translate({cx:g} {cy:g}) skewX(-{S_SKEW}) translate({-cx:g} {-cy:g})" fill="none" '
            'stroke-linecap="round" stroke-linejoin="round">'
            f'<use href="#s" stroke="url(#c)" stroke-width="{S_CHROME_W}" filter="url(#d)"/>'
            f'<use href="#s" stroke="{mix(CHILI, "#000000", 0.55)}" stroke-opacity=".7" stroke-width="{S_EDGE_W}"/>'
            f'<use href="#s" stroke="url(#r)" stroke-width="{S_RED_W}"/>'
            f'<use href="#s" stroke="#fff" stroke-opacity=".28" stroke-width="{S_SHINE_W}"/>'
            '</g></svg>')


# ---- backgrounds ---------------------------------------------------------------------------------------------------
def bonnet_stripes(stripe, pin, pin_w=2):
    """Two stripes with a white pinstripe on both edges, symmetric about the middle."""
    def one(a, b):
        return [f"transparent calc({a}% - {pin_w}px)", f"{pin} calc({a}% - {pin_w}px)", f"{pin} {a}%",
                f"{stripe} {a}%", f"{stripe} {b}%", f"{pin} {b}%", f"{pin} calc({b}% + {pin_w}px)",
                f"transparent calc({b}% + {pin_w}px)"]
    stops = ["transparent 0"] + one(31, 39) + one(61, 69) + ["transparent 100%"]
    return f"linear-gradient(90deg, {', '.join(stops)}) fixed"


def page_background(dark, urls):
    if dark:
        paint = (f"radial-gradient(ellipse 120% 90% at 18% 0%, {ISLAND_HI} 0%, {ISLAND} 38%, {ISLAND_LO} 100%) fixed")
        stripes = bonnet_stripes(rgbs_alpha(STRIPE, 0.88), rgbs_alpha(PIN, 0.7))
    else:
        paint = "radial-gradient(ellipse 120% 90% at 18% 0%, #eef4f9 0%, #cfdeeb 45%, #a9c3da 100%) fixed"
        stripes = bonnet_stripes(rgbs_alpha(STRIPE, 0.82), rgbs_alpha("#ffffff", 0.95))
    return ", ".join([
        f"{roof_gradient()} left 0 top var(--header-height, 56px) / 100% 5px no-repeat fixed",   # the ombre roof, just under the header
        f"url('{urls['badge']}') right 24px bottom 18px / 54px auto no-repeat fixed",
        f"url('{urls['flake']}') 0 0 / 180px 180px fixed",
        stripes,
        paint,
    ])


def rgbs_alpha(h, a):
    return f"rgba({rgbs(h)}, {a})"


def card_background(dark, urls):
    base = "#111419" if dark else "#f7f9fc"
    return ", ".join([
        f"{roof_gradient()} left top / 100% 4px no-repeat",
        f"url('{urls['flake'] if dark else urls['flake_light']}') 0 0 / 180px 180px",
        f"linear-gradient(180deg, {'rgba(255,255,255,.035)' if dark else 'rgba(255,255,255,.7)'}, transparent 60%)",
        base,
    ])


# ---- variables -----------------------------------------------------------------------------------------------------
def mode_vars(dark, urls):
    p = CHILI_DARK if dark else CHILI
    card = "#111419" if dark else "#f7f9fc"
    page = ISLAND_LO if dark else "#cfdeeb"
    text = "#eef3f8" if dark else "#0f2133"
    text2 = "#a7b6c6" if dark else "#40566b"
    v = {
        "primary-color": p,
        "dark-primary-color": mix(p, "#000000", 0.25),
        "light-primary-color": mix(p, "#ffffff", 0.45),
        "accent-color": ROOF[0] if dark else ROOF[1],
        "text-primary-color": "#ffffff",
        "primary-background-color": page,
        "secondary-background-color": mix(page, card, 0.5),
        "card-background-color": card,
        "ha-card-background": card_background(dark, urls),
        "ha-card-border-color": "rgba(255,255,255,.07)" if dark else "rgba(15,33,51,.10)",
        "ha-card-border-width": "1px",
        "ha-card-border-radius": "20px",
        "ha-card-box-shadow": ("0 1px 0 rgba(255,255,255,.04) inset, 0 2px 4px rgba(0,0,0,.35), 0 14px 30px rgba(4,14,26,.45)"
                               if dark else
                               "0 1px 0 #fff inset, 0 1px 2px rgba(15,33,51,.10), 0 10px 24px rgba(15,33,51,.12)"),
        "ha-dialog-surface-background": card,
        "lovelace-background": page_background(dark, urls),
        "app-header-background-color": JET,
        "app-header-text-color": "#f2f5f8",
        "app-header-border-bottom": "none",
        "app-header-edit-background-color": mix(JET, CHILI, 0.35),
        "app-header-edit-text-color": "#ffffff",
        "sidebar-background-color": "#0e1014" if dark else "#f3f6f9",
        "sidebar-text-color": "#c3ccd6" if dark else "#3b4b5c",
        "sidebar-icon-color": "#8f9aa6" if dark else "#5d6d7e",
        "sidebar-selected-icon-color": p,
        "sidebar-selected-text-color": "#ffffff" if dark else "#0f2133",
        "sidebar-menu-button-text-color": "#f2f5f8" if dark else "#0f2133",
        "primary-text-color": text,
        "secondary-text-color": text2,
        "disabled-text-color": mix(text2, card, 0.45),
        "divider-color": "rgba(255,255,255,.09)" if dark else "rgba(15,33,51,.12)",
        "state-icon-color": "#b9c6d3" if dark else "#3f5468",
        "state-active-color": p,
        "state-switch-active-color": p,
        "state-input_boolean-active-color": p,
        "state-fan-active-color": ROOF[0],
        "state-light-active-color": "#ffd277" if dark else "#e7a31c",      # halo-white-warm, not red
        "state-climate-heat-color": "#ff8a3d",
        "state-climate-cool-color": ROOF[0],
        "switch-checked-color": p,
        "switch-checked-button-color": p,
        "switch-checked-track-color": p,
        "slider-color": p,
        "success-color": "#35c46b" if dark else "#23944f",
        "warning-color": "#ffb23e" if dark else "#b8700c",
        "error-color": "#ff6b4a" if dark else "#c43d1f",                   # orange-red, so it reads apart from the S red
        "info-color": ROOF[0] if dark else ROOF[1],
        "code-editor-background-color": "#0c0e12" if dark else "#eef2f6",
        "markdown-code-background-color": "#1b2028" if dark else "#e7edf3",
        "data-table-background-color": card,
        "scrollbar-thumb-color": "#3a4552" if dark else "#a9b7c5",
        "mini-island-blue": ISLAND,
        "mini-roof-gradient": roof_gradient(),
        "mini-chili-red": CHILI,
        "graph-color-1": ROOF[0] if dark else ROOF[1],
        "graph-color-2": p,
        "graph-color-3": "#ffb23e",
        "graph-color-4": "#9fb3c8",
        "graph-color-5": "#35c46b",
        "graph-color-6": text,
        "graph-color-7": "#b07cff",
        "graph-color-8": "#2ec4b6",
        "mdc-theme-primary": p,
        "mdc-theme-secondary": ROOF[0],
    }
    for step, t in ((5, -0.85), (10, -0.75), (20, -0.55), (30, -0.3), (40, -0.12), (50, 0.0), (60, 0.2), (70, 0.4),
                    (80, 0.6), (90, 0.8), (95, 0.9)):
        v[f"ha-color-primary-{step:02d}"] = mix(p, "#000000", -t) if t < 0 else mix(p, "#ffffff", t)
    for key in ("primary-color", "accent-color", "primary-text-color", "secondary-text-color", "disabled-text-color",
                "text-primary-color", "primary-background-color", "card-background-color", "state-icon-color",
                "success-color", "warning-color", "error-color", "info-color"):
        v[f"rgb-{key}"] = rgbs(v[key])
    return v


def block(d, indent):
    return "".join(f'{" " * indent}{k}: "{val}"\n' for k, val in d.items())


def data_uri(svg):
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def build():
    urls = {"flake": data_uri(flake_svg(6, -4.75)), "flake_light": data_uri(flake_svg(5, -3.95)),
            "badge": data_uri(s_badge_svg())}
    return ("# Generated by tools/build_theme.py (https://github.com/edwork/mini-cooper-s-theme).\n"
            "# Edit the generator, not this file.\n"
            "# 2022 MINI Cooper S: Island Blue, Multitone roof, black bonnet stripes, Chili Red S.\n"
            '"Mini Cooper S":\n  modes:\n    light:\n' + block(mode_vars(False, urls), 6)
            + "    dark:\n" + block(mode_vars(True, urls), 6))


def main():
    text = build()
    if "--check" in sys.argv:
        if not THEME.exists() or THEME.read_text() != text:
            sys.exit(f"{THEME.relative_to(REPO)} is out of date: run python3 tools/build_theme.py")
        print(f"{THEME.relative_to(REPO)} is up to date")
        return
    THEME.write_text(text)
    print(f"wrote {THEME.relative_to(REPO)} ({len(text) // 1024} KB)")


if __name__ == "__main__":
    main()
