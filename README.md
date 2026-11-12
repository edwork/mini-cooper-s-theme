# Mini Cooper S

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/docs/faq/custom_repositories/)
[![Validate](https://github.com/edwork/mini-cooper-s-theme/actions/workflows/validate.yml/badge.svg)](https://github.com/edwork/mini-cooper-s-theme/actions/workflows/validate.yml)
[![Open your Home Assistant instance and open this repository in HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=edwork&repository=mini-cooper-s-theme&category=theme)

A Home Assistant theme after a 2022 MINI Cooper S in Island Blue with the Multitone roof: metallic blue paint,
the blue-to-black roof fade, black bonnet stripes and the red S badge. It has light and dark modes.

![Mini Cooper S in dark mode](docs/images/preview-dark.webp)

![Mini Cooper S in light mode](docs/images/preview-light.webp)

## Design

| On the car | In the theme |
|---|---|
| Island Blue metallic paint | The page: a blue sheen with metallic flake |
| Multitone roof, bright blue at the windshield fading to Jet Black | A band under the header and a strip along the top of every card |
| Black bonnet stripes with a white pinstripe | Two stripes down the page, like looking over the bonnet |
| Chili Red S on the grille | The primary colour for anything that's on, and an S badge in the bottom-right corner |
| Jet Black roof and piano-black trim | The header and sidebar, and the cards in dark mode |
| Round LED headlights | Rounder, 20 px cards |

Light mode uses pale Island Blue with pearl cards; dark mode is Island Blue at night with piano-black cards. Error
colours are orange-red, so they read apart from the S red.

It's plain theme variables: no card-mod or other add-ons needed. The flake and the badge are SVGs embedded in the
theme file, so there's nothing to copy into `www/`.

## Installation

### HACS

1. HACS → ⋮ → **Custom repositories**. Add `https://github.com/edwork/mini-cooper-s-theme` with type **Theme**.
2. Search for **Mini Cooper S**, then **Download**.
3. Run the **Home Assistant Frontend: Reload themes** action (`frontend.reload_themes`), or restart.

### Manual

Copy [`themes/mini_cooper_s.yaml`](themes/mini_cooper_s.yaml) into your `config/themes/` folder, then reload themes.

Either way, your `configuration.yaml` needs to load themes from that folder:

```yaml
frontend:
  themes: !include_dir_merge_named themes
```

## Usage

- **Your profile:** your user (bottom left) → **Theme** → **Mini Cooper S**. It follows your light/dark setting.
- **One view:** edit the view → **Theme**, or `theme: Mini Cooper S` in YAML. A view theme styles the view's
  content; the header and sidebar keep your profile theme.

## Customising

`themes/mini_cooper_s.yaml` is generated, so don't edit it by hand. The paint colours (body, roof stops, stripe,
pinstripe, badge) are constants at the top of [`tools/build_theme.py`](tools/build_theme.py). Change them and run:

```sh
python3 tools/build_theme.py            # regenerate themes/mini_cooper_s.yaml
python3 tools/build_theme.py --check    # what CI runs: fails if the YAML is out of date
```

It needs only Python 3.9+ and the standard library.

## Credits

MINI and Cooper S are trademarks of BMW AG. This is an unofficial fan project and isn't affiliated with or endorsed
by BMW or MINI.

## License

[MIT](LICENSE)
