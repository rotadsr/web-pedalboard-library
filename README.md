# Web Pedalboard Library

A browser-based pedalboard builder for visualising and documenting guitar signal chains. Add pedals, amps, guitars, and cabinets to a canvas, connect them with cables, adjust knobs and switches, and save named presets.

## Features

- **Visual canvas** — drag nodes freely, connect ports with colour-coded cables, zoom and pan
- **Real pedal images** — pedals and amps render as photos with interactive knob/slider/switch overlays placed on top of the actual hardware image
- **Layout Editor** — built-in tool for placing controls on any pedal or amp image without leaving the app
- **Presets** — save, load, rename and delete named signal chains; state persists in `localStorage`
- **Undo** — up to 40 steps
- **Cable management** — click a cable to change its colour (orange, yellow, blue, red, green); drag the midpoint handle to reroute it; double-click to delete
- **Background removal** — white/near-white backgrounds are automatically stripped from JPG images using a border-seeded flood fill

## Collection stats

| Category | Count |
|----------|-------|
| Pedals   | 262   |
| Amps     | 5     |
| Guitars  | 15    |
| Basses   | 17    |
| Cabinets | 15    |

**Brands covered:** Aguilar · Boss · Darkglass · DigiTech · Dunlop · Electro-Harmonix · ENGL · Eventide · Fulltone · Ibanez · Klon · Line 6 · Marshall · Mesa/Boogie · Morley · MXR · Origin Effects · ProCo · Strymon · TC Electronic · Tech 21

## Project structure

```
index.html                  Single-file app (HTML + CSS + JS)
collections/
  manifest.json             Ordered list of collection files to load
  boss.json                 Example collection file
  *.json                    One file per brand
  images/                   Pedal/amp/guitar PNG and JPG photos
  logos/                    Brand SVG logos
dev-server.py               Local dev server (not needed for deployment)
```

## Running locally

Open `index.html` directly in a browser — no build step required.

To use the Layout Editor's **Save** button (which writes layout JSON back to collection files), run the dev server instead:

```bash
python3 dev-server.py
# → http://localhost:3456/index.html
```

Requires Python 3.6+, no dependencies.

## Deploying to GitHub Pages

Push the following files — everything else is optional:

```
index.html
collections/manifest.json
collections/*.json
collections/images/
collections/logos/
```

`dev-server.py` is not needed on GitHub Pages.

## Collection JSON format

Each collection file follows this structure:

```json
{
  "brand": "Boss",
  "pedals": {
    "bd2": {
      "name": "BD-2 Blues Driver",
      "cat": "Gain/Drive",
      "inst": "guitar",
      "color": "#1a1a2a",
      "knobs": [
        { "id": "level", "label": "Level", "def": 0.5 },
        { "id": "tone",  "label": "Tone",  "def": 0.5 },
        { "id": "gain",  "label": "Gain",  "def": 0.5 }
      ],
      "layout": {
        "image": "boss-bd-2.jpg",
        "removeWhiteBg": true,
        "widthMm": 73,
        "heightMm": 129,
        "controls": {
          "level": { "x": 0.68, "y": 0.35 },
          "tone":  { "x": 0.32, "y": 0.45 },
          "gain":  { "x": 0.50, "y": 0.55 }
        }
      }
    }
  }
}
```

### `layout.controls` control types

| `type`     | Description                          | Extra fields |
|------------|--------------------------------------|--------------|
| *(omitted)*| Knob (default)                       | `knobSize` (fraction of card width) |
| `slider`   | Vertical or horizontal fader         | `sliderSize`, `orientation` (`v`/`h`) |
| `toggle`   | Multi-position toggle switch         | `opts` (array), `orientation` (`v`/`h`) |
| `cycle`    | Click-to-cycle value selector        | `opts` (array) |
| `fs`       | Footswitch (on/off)                  | — |
| `port-in`  | Input jack (visual only)             | `label` |
| `port-out` | Output jack (visual only)            | `label` |

All `x`/`y` values are normalised 0–1 fractions of the image dimensions.

### `removeWhiteBg`

Set to `true` on any entry whose image has a white or near-white background (typically JPGs). The app strips the background using a flood-fill algorithm at render time. PNG images with existing transparency do not need this flag.
