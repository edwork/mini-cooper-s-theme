#!/usr/bin/env python3
"""Mini Cooper S themes for Home Assistant, after the 2022 MINI Cooper S and its best-known paints.

The car's details, and where each one goes:
  - Body paint                      -> the page: a metallic sheen with flake
  - Roof (Multitone, white, black   -> the band under the header, and the strip along each card's top edge
    or Chili Red)
  - Bonnet stripes and pinstripes   -> two fixed stripes down the page, like looking over the bonnet
  - Chili Red "S" grille badge      -> the primary/active colour in every colourway (every Cooper S wears it), and a
                                       chrome-edged S badge at the page's bottom right
  - Jet Black roof / piano trim     -> the header, sidebar and (dark mode) cards
  - Round LED halo headlights       -> rounder cards (20 px)

Themes (each has light and dark modes):
  - "Mini Cooper S": Island Blue with the Multitone roof (the original; the name is kept so existing setups work).
  - "Mini Cooper S British Racing Green", "... Chili Red", "... Midnight Black", "... Pepper White", "... Zesty Yellow".
Colourways are the SCHEMES table below; add one there. Paint colours are matched by eye from photos, not official.

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

CHILI = "#d72631"           # S badge
CHILI_DARK = "#e23a44"      # S badge, lifted for dark backgrounds
CHROME = ["#f4f6f8", "#a9b0b8", "#e3e7eb", "#7d858e"]
JET = "#0b0c0f"
STRIPE_BLACK = "#16181c"
COOL_BLUE = "#4aa3ff"       # climate "cool" where the paint has no blue of its own

ROOF_MULTITONE = ["#3d8fe3", "#2b62b8", "#1d2f63", "#11152a", "#0a0a0d"]   # windshield -> spoiler
ROOF_WHITE = ["#ffffff", "#e4e8eb", "#f6f8f9", "#d5dbe0"]
ROOF_BLACK = ["#3a3d44", "#16181c", "#0b0c0f"]
ROOF_CHILI = ["#ee4a54", CHILI, "#a51b25"]

# Island Blue's neutrals, tuned by hand (the other colourways derive theirs from a tint; see neutrals()).
ISLAND_NEUTRALS = {
    True: dict(card="#111419", text="#eef3f8", text2="#a7b6c6", border="rgba(255,255,255,.07)",
               shadow="0 1px 0 rgba(255,255,255,.04) inset, 0 2px 4px rgba(0,0,0,.35), 0 14px 30px rgba(4,14,26,.45)",
               sidebar="#0e1014", sidebar_text="#c3ccd6", sidebar_icon="#8f9aa6", sidebar_sel="#ffffff",
               menu="#f2f5f8", divider="rgba(255,255,255,.09)", icon="#b9c6d3", code="#0c0e12", md_code="#1b2028",
               scrollbar="#3a4552", card_glaze="rgba(255,255,255,.035)"),
    False: dict(card="#f7f9fc", text="#0f2133", text2="#40566b", border="rgba(15,33,51,.10)",
                shadow="0 1px 0 #fff inset, 0 1px 2px rgba(15,33,51,.10), 0 10px 24px rgba(15,33,51,.12)",
                sidebar="#f3f6f9", sidebar_text="#3b4b5c", sidebar_icon="#5d6d7e", sidebar_sel="#0f2133",
                menu="#0f2133", divider="rgba(15,33,51,.12)", icon="#3f5468", code="#eef2f6", md_code="#e7edf3",
                scrollbar="#a9b7c5", card_glaze="rgba(255,255,255,.7)"),
}

# One row per colourway. paint = (highlight, mid, shadow) for each mode's page; stripe/pin = (dark, light) colour and
# opacity; accent = (dark, light), also fans unless `fan` is set; flake = (dark, light) (alpha gain, bias); tint colours the derived neutrals.
SCHEMES = [
    dict(name="Mini Cooper S", paint_name="Island Blue", roof_name="Multitone roof",
         dark=("#4d86b3", "#2f6690", "#173650"), light=("#eef4f9", "#cfdeeb", "#a9c3da"), roof=ROOF_MULTITONE,
         stripe=((STRIPE_BLACK, .88), (STRIPE_BLACK, .82)), pin=(("#eef2f6", .7), ("#ffffff", .95)),
         accent=("#3d8fe3", "#2b62b8"), fan="#3d8fe3", cool="#3d8fe3", flake=((6, -4.75), (6, -4.75)), neutrals=ISLAND_NEUTRALS),
    dict(name="Mini Cooper S British Racing Green", paint_name="British Racing Green", roof_name="white roof",
         dark=("#2f6b52", "#1a4a37", "#0b261c"), light=("#eef5f1", "#d3e4da", "#a9c8b6"), roof=ROOF_WHITE,
         stripe=(("#eef1f3", .2), ("#ffffff", .9)), pin=(("#eef1f3", .45), ("#1a4a37", .45)),
         accent=("#6cc59a", "#2e7d57"), cool=COOL_BLUE, flake=((6, -4.8), (5, -3.95)), tint="#1a4a37"),
    dict(name="Mini Cooper S Chili Red", paint_name="Chili Red", roof_name="white roof",
         dark=("#d8434c", "#a81c25", "#4a0b10"), light=("#f9e6e7", "#eab9bc", "#d17d83"), roof=ROOF_WHITE,
         stripe=(("#eef1f3", .2), ("#ffffff", .9)), pin=(("#eef1f3", .45), ("#a81c25", .4)),
         accent=("#e9edf0", "#59606a"), cool=COOL_BLUE, flake=((6, -4.8), (5, -3.95)), tint="#5a3b3d"),
    dict(name="Mini Cooper S Midnight Black", paint_name="Midnight Black", roof_name="Chili Red roof",
         dark=("#3a3e46", "#1d2026", "#0a0b0e"), light=("#f3f4f6", "#dfe2e6", "#c2c7cd"), roof=ROOF_CHILI,
         stripe=((STRIPE_BLACK, .7), (STRIPE_BLACK, .82)), pin=((CHILI_DARK, .75), (CHILI, .85)),
         accent=("#c7ccd3", "#5b6470"), cool=COOL_BLUE, flake=((6.5, -4.6), (5, -3.95)), tint="#2a3240"),
    dict(name="Mini Cooper S Pepper White", paint_name="Pepper White", roof_name="black roof",
         dark=("#62666d", "#3b3e44", "#1c1e22"), light=("#ffffff", "#eeefec", "#d6d8d4"), roof=ROOF_BLACK,
         stripe=((STRIPE_BLACK, .85), (STRIPE_BLACK, .85)), pin=(("#ffffff", .45), ("#ffffff", .9)),
         accent=("#9fb3c8", "#4f6378"), cool=COOL_BLUE, flake=((6, -4.75), (4, -3.3)), tint="#4a5058"),
    dict(name="Mini Cooper S Zesty Yellow", paint_name="Zesty Yellow", roof_name="black roof",
         dark=("#c4a514", "#7d6a08", "#2c2504"), light=("#fffbe2", "#f9ec9c", "#ecd24a"), roof=ROOF_BLACK,
         stripe=((STRIPE_BLACK, .85), (STRIPE_BLACK, .85)), pin=((STRIPE_BLACK, 0), (STRIPE_BLACK, 0)),
         accent=("#f2d230", "#8a6f00"), cool=COOL_BLUE, flake=((6, -4.75), (4, -3.3)), tint="#5a5230"),
]


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


def roof_gradient(roof, angle="90deg"):
    stops = ", ".join(f"{c} {round(i * 100 / (len(roof) - 1))}%" for i, c in enumerate(roof))
    return f"linear-gradient({angle}, {stops})"


def neutrals(tint, dark):
    """Card, text, sidebar and chrome greys, warmed or cooled slightly towards the paint."""
    if dark:
        return dict(card=mix("#0f1013", tint, .06), text=mix("#f2f4f7", tint, .05), text2=mix("#aab0b8", tint, .15),
                    border="rgba(255,255,255,.07)",
                    shadow=f"0 1px 0 rgba(255,255,255,.04) inset, 0 2px 4px rgba(0,0,0,.35), "
                           f"0 14px 30px rgba({rgbs(mix('#000000', tint, .2))},.45)",
                    sidebar=mix("#0d0e11", tint, .04), sidebar_text=mix("#c6cbd1", tint, .1),
                    sidebar_icon=mix("#8f959c", tint, .12), sidebar_sel="#ffffff", menu="#f2f5f8",
                    divider="rgba(255,255,255,.09)", icon=mix("#bcc3cb", tint, .15), code=mix("#0c0d10", tint, .04),
                    md_code=mix("#1c1f24", tint, .06), scrollbar=mix("#3a3f46", tint, .15),
                    card_glaze="rgba(255,255,255,.035)")
    ink = mix("#14171b", tint, .2)
    return dict(card=mix("#f8f9fa", tint, .02), text=ink, text2=mix("#4a5058", tint, .2),
                border=f"rgba({rgbs(ink)},.10)",
                shadow=f"0 1px 0 #fff inset, 0 1px 2px rgba({rgbs(ink)},.10), 0 10px 24px rgba({rgbs(ink)},.12)",
                sidebar=mix("#f4f5f7", tint, .03), sidebar_text=mix("#3d434a", tint, .15),
                sidebar_icon=mix("#5f666e", tint, .15), sidebar_sel=ink, menu=ink, divider=f"rgba({rgbs(ink)},.12)",
                icon=mix("#434a52", tint, .2), code=mix("#eff1f3", tint, .03), md_code=mix("#e8ebee", tint, .05),
                scrollbar=mix("#aab0b7", tint, .15), card_glaze="rgba(255,255,255,.7)")


def scheme_neutrals(sc, dark):
    return sc["neutrals"][dark] if "neutrals" in sc else neutrals(sc["tint"], dark)


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


def page_background(sc, dark, urls):
    hi, mid, lo = sc["dark" if dark else "light"]
    paint = f"radial-gradient(ellipse 120% 90% at 18% 0%, {hi} 0%, {mid} {38 if dark else 45}%, {lo} 100%) fixed"
    (stripe, sa), (pin, pa) = sc["stripe"][0 if dark else 1], sc["pin"][0 if dark else 1]
    stripes = bonnet_stripes(rgbs_alpha(stripe, sa), rgbs_alpha(pin, pa))
    return ", ".join([
        f"{roof_gradient(sc['roof'])} left 0 top var(--header-height, 56px) / 100% 5px no-repeat fixed",   # roof, under the header
        f"url('{urls['badge']}') right 24px bottom 18px / 54px auto no-repeat fixed",
        f"url('{urls['flake' if dark else 'flake_light']}') 0 0 / 180px 180px fixed",
        stripes,
        paint,
    ])


def rgbs_alpha(h, a):
    return f"rgba({rgbs(h)}, {a})"


def card_background(sc, dark, urls):
    n = scheme_neutrals(sc, dark)
    return ", ".join([
        f"{roof_gradient(sc['roof'])} left top / 100% 4px no-repeat",
        f"url('{urls['card_flake'] if dark else urls['card_flake_light']}') 0 0 / 180px 180px",
        f"linear-gradient(180deg, {n['card_glaze']}, transparent 60%)",
        n["card"],
    ])


# ---- variables -----------------------------------------------------------------------------------------------------
def mode_vars(sc, dark, urls):
    n = scheme_neutrals(sc, dark)
    p = CHILI_DARK if dark else CHILI
    card, text, text2 = n["card"], n["text"], n["text2"]
    page = sc["dark"][2] if dark else sc["light"][1]
    accent = sc["accent"][0 if dark else 1]
    v = {
        "primary-color": p,
        "dark-primary-color": mix(p, "#000000", 0.25),
        "light-primary-color": mix(p, "#ffffff", 0.45),
        "accent-color": accent,
        "text-primary-color": "#ffffff",
        "primary-background-color": page,
        "secondary-background-color": mix(page, card, 0.5),
        "card-background-color": card,
        "ha-card-background": card_background(sc, dark, urls),
        "ha-card-border-color": n["border"],
        "ha-card-border-width": "1px",
        "ha-card-border-radius": "20px",
        "ha-card-box-shadow": n["shadow"],
        "ha-dialog-surface-background": card,
        "lovelace-background": page_background(sc, dark, urls),
        "app-header-background-color": JET,
        "app-header-text-color": "#f2f5f8",
        "app-header-border-bottom": "none",
        "app-header-edit-background-color": mix(JET, CHILI, 0.35),
        "app-header-edit-text-color": "#ffffff",
        "sidebar-background-color": n["sidebar"],
        "sidebar-text-color": n["sidebar_text"],
        "sidebar-icon-color": n["sidebar_icon"],
        "sidebar-selected-icon-color": p,
        "sidebar-selected-text-color": n["sidebar_sel"],
        "sidebar-menu-button-text-color": n["menu"],
        "primary-text-color": text,
        "secondary-text-color": text2,
        "disabled-text-color": mix(text2, card, 0.45),
        "divider-color": n["divider"],
        "state-icon-color": n["icon"],
        "state-active-color": p,
        "state-switch-active-color": p,
        "state-input_boolean-active-color": p,
        "state-fan-active-color": sc.get("fan", accent),        # Island Blue keeps one blue in both modes
        "state-light-active-color": "#ffd277" if dark else "#e7a31c",      # halo-white-warm, not red
        "state-climate-heat-color": "#ff8a3d",
        "state-climate-cool-color": sc["cool"],
        "switch-checked-color": p,
        "switch-checked-button-color": p,
        "switch-checked-track-color": p,
        "slider-color": p,
        "success-color": "#35c46b" if dark else "#23944f",
        "warning-color": "#ffb23e" if dark else "#b8700c",
        "error-color": "#ff6b4a" if dark else "#c43d1f",                   # orange-red, so it reads apart from the S red
        "info-color": accent,
        "code-editor-background-color": n["code"],
        "markdown-code-background-color": n["md_code"],
        "data-table-background-color": card,
        "scrollbar-thumb-color": n["scrollbar"],
        "mini-paint-color": sc["dark"][1],
        "mini-roof-gradient": roof_gradient(sc["roof"]),
        "mini-chili-red": CHILI,
        "graph-color-1": accent,
        "graph-color-2": p,
        "graph-color-3": "#ffb23e",
        "graph-color-4": "#9fb3c8",
        "graph-color-5": "#35c46b",
        "graph-color-6": text,
        "graph-color-7": "#b07cff",
        "graph-color-8": "#2ec4b6",
        "mdc-theme-primary": p,
        "mdc-theme-secondary": sc.get("fan", accent),
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
    badge = data_uri(s_badge_svg())
    out = ["# Generated by tools/build_theme.py (https://github.com/edwork/mini-cooper-s-theme).\n",
           "# Edit the generator, not this file.\n",
           "# 2022 MINI Cooper S colourways: paint, roof, bonnet stripes, and the Chili Red S.\n"]
    for sc in SCHEMES:
        (dg, db), (lg, lb) = sc["flake"]
        urls = {"badge": badge, "flake": data_uri(flake_svg(dg, db)), "flake_light": data_uri(flake_svg(lg, lb)),
                "card_flake": data_uri(flake_svg(6, -4.75)), "card_flake_light": data_uri(flake_svg(5, -3.95))}
        out.append(f"# {sc['name']}: {sc['paint_name']}, {sc['roof_name']}.\n"
                   f'"{sc["name"]}":\n  modes:\n    light:\n' + block(mode_vars(sc, False, urls), 6)
                   + "    dark:\n" + block(mode_vars(sc, True, urls), 6))
    return "".join(out)


def main():
    text = build()
    if "--check" in sys.argv:
        if not THEME.exists() or THEME.read_text() != text:
            sys.exit(f"{THEME.relative_to(REPO)} is out of date: run python3 tools/build_theme.py")
        print(f"{THEME.relative_to(REPO)} is up to date")
        return
    THEME.write_text(text)
    print(f"wrote {THEME.relative_to(REPO)} ({len(text) // 1024} KB, {len(SCHEMES)} themes)")


if __name__ == "__main__":
    main()
