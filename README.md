# Wildcard Deck

**Language:** English | [日本語](README.ja.md)

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/UI-PySide6-41CD52)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&logoColor=white)
![Status](https://img.shields.io/badge/Version-2.5-orange)

**Category:** Wildcard Desktop Manager
**Features:** Create, edit, organize, and search wildcards

A desktop app for managing Stable Diffusion wildcards in one place.

Wildcard Deck keeps a growing collection of `.txt` wildcard files organized, searchable, and visual — with thumbnails, custom tags, favorites, LoRA awareness, and thumbnail generation via the sd-webui API, all from a single GUI built with PySide6.

> Primarily developed and tested on Windows.

## Features

### Library & Search

- Load, edit, and save `.txt` wildcard files
- Browse by folder tree, with per-folder counts
- Search across file names, file contents, custom tags, and LoRA names
- Copy with or without LoRA tags
- Import (copy / move) from `sd-dynamic-prompts` and `wildcard-gallery` libraries
- Rename cards from the right-click menu
- Explorer-style range selection with Shift+click / drag rectangle
- Create, rename, and move folders from the folder tree (drag & drop supported)

### Thumbnails & Gallery

- Thumbnail grid for the whole library
- Generate thumbnails through a StabilityMatrix / Forge-style sd-webui API (`sdapi`) and save them as `.webp`
- Assign any existing image as a thumbnail — no generation required
- Add multiple images per card (2nd, 3rd, …) and flip through them with a double-click flip animation (`2/3` pill shows the position; Ctrl+double-click still copies the full text)
- Delete only the thumbnail image(s) — by page, from the right-click menu — without deleting the wildcard itself (sent to the Recycle Bin / Trash, so it can be recovered)
- Batch-generate missing thumbnails in a background thread without freezing the UI
- Combine random wildcards during generation for more varied previews

### Creating Wildcards

- Character tab plus dynamic custom tabs (add your own with “+”)
- Build and manage prompts per outfit / variation
- Preview thumbnails inside the creation dialog
- Color-coded LoRA tags, so LoRAs in use are visible at a glance
- Tag delete mode with clear visual state (button and border color)

### Favorites & LoRA / Base Model

- Star favorites and filter to them from the folder tree
- Automatic base-model detection for LoRAs from `cm-info.json` and safetensors headers
- Base-model badges on cards — `ill` (Illustrious), `ani` (Anima), `mix` — and filtering by base model
- List of LoRAs you have not created a wildcard for yet, filterable by base model

### sd-webui API Integration

- Connection test with JSON response validation
- Fetch the checkpoint list
- Live generation status in the API status indicator
- ADetailer support

## Storage Layout

```text
library/
├── wildcards/                    # Wildcard files (.txt)
│   └── Position/
│       ├── character1.txt
│       └── character1.txt.wcm.json   # Custom tags (sidecar)
└── thumbnails/                   # Thumbnails (.webp)
    └── Position/
        ├── character1.preview.webp   # 1st image
        └── character1.g2.webp        # 2nd and later images (.g3, .g4, …)

wildcard_manager.db   # SQLite index (for fast browsing of large libraries)
config.json           # Settings
ui_state.json         # UI state (sort order, splitter positions, …)
```

Custom tags are stored in a sidecar `.wcm.json` file next to each `.txt`, so your wildcard files themselves stay plain text and portable.

## Getting Started

### Requirements

- Windows (recommended / primarily tested)
- Python 3.10+
- PySide6, Pillow, requests — see `requirements.txt`

### Install

```bash
git clone https://github.com/rock000914/wildcard-deck.git
cd wildcard-deck
pip install -r requirements.txt
```

### Run

```bash
python app.py
```

On Windows you can also double-click `run_wildcard_manager.bat`, which launches the app without a console window.

### Languages

Choose **Settings → General → Language** to switch between 日本語, English, 한국어, and 中文（简体）.
The choice is saved as `ui_language` in `config.json` and applies immediately without a restart.
Translations live in `wildcard_manager/i18n/<code>.json` (keyed by the Japanese source text);
strings without a translation fall back to Japanese.

## First-Time Setup

1. Open the **Settings** tab and check:

   - **Library root** — where wildcards are stored (default: `library/wildcards`)
   - **Thumbnail root** — where thumbnails are stored (default: `library/thumbnails`)
   - **API base URL** — your sd-webui API endpoint (default: `http://127.0.0.1:7860`)
   - **Import source paths** — existing `sd-dynamic-prompts` / `wildcard-gallery` folders, if you have them

2. Click **Reload** to scan your library.

Thumbnail generation requires a running sd-webui-compatible API (e.g. AUTOMATIC1111, Forge, or StabilityMatrix). Browsing, searching, editing, and assigning existing images as thumbnails work without it.

## Project Structure

| File | Role |
| --- | --- |
| `app.py` | Entry point |
| `wildcard_manager/main_window.py` | Main window |
| `wildcard_manager/api.py` | sd-webui API client |
| `wildcard_manager/repository.py` | SQLite + filesystem operations |
| `wildcard_manager/models.py` | Data models (`AppSettings`, `WildcardEntry`) |
| `wildcard_manager/config.py` | Settings persistence |
| `wildcard_manager/i18n.py` | UI language switching (widget translation, catalog loading) |
| `wildcard_manager/i18n/*.json` | English / Korean / Chinese translation catalogs |
| `wildcard_manager/theme.py` | Design system — colors, dimensions, widget builders (single source for appearance) |
| `wildcard_manager/icons.py` | Line icons drawn at 2x resolution |
| `wildcard_manager/thumbnail_model.py` | Thumbnail list model and delegate |
| `wildcard_manager/thumbnail_workers.py` | Thumbnail loading workers |
| `wildcard_manager/single_thumbnail_worker.py` | Single-thumbnail generation worker |
| `wildcard_manager/workers.py` | Background workers |
| `wildcard_manager/widgets.py` | Shared widgets |
| `wildcard_manager/tag_editor.py` | Tag editor widget |
| `wildcard_manager/new_wildcard_dialog.py` | New-wildcard creation dialog |
| `wildcard_manager/settings_dialog.py` | Settings dialog |
| `wildcard_manager/ui_utils.py` | File-manager helpers and shared context menus |
| `wildcard_manager/logging_setup.py` | Logging setup |

## Roadmap

- Automated tests
- Migrate the large list view to `QAbstractTableModel + QTableView` for even larger libraries
- Batch rename for wildcards
- Monitor multiple API endpoints at once
- Rule-based automatic thumbnail generation
- Dark / light theme toggle
- Export to CSV / JSON

## Known Limitations

- The GUI is PySide6-based; a table-model migration is planned if list performance becomes a bottleneck at very large scale.
- Test coverage is still limited — some paths are not yet covered by automated tests.
- Windows is the primary target; some features (e.g. opening the file manager, path handling) are Windows-oriented.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a summary of each release. The full, detailed development history (in Japanese) is preserved in [README.ja.md](README.ja.md).

Current release: **v2.5 (2026-11-03)** — UI redesign with a professional asset-browser design system, prompt-tag copy/search actions, multi-image thumbnails with flip animation, and assigning existing images as thumbnails.

## License

Not yet specified (TBD).
