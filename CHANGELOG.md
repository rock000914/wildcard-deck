# Changelog

**Language:** English | [日本語 (full detailed history)](README.ja.md)

All notable changes to Wildcard Manager are summarized here.
The full development notes — including implementation details and verification results — are preserved in Japanese in [README.ja.md](README.ja.md).

## v2.5 — 2026-11-03 — UI Redesign

A visual redesign only, modeled on professional asset browsers. Existing workflows were not changed, except for the new prompt-tag actions below.

- New design system in `theme.py`: dark navy palette, 8px spacing grid, unified 36px controls, and shared widget builders as the single source for appearance
- New `icons.py`: emoji icons replaced with 16px line icons drawn at 2x resolution
- Hardcoded colors removed across dialogs and widgets; remaining colors are data colors (base-model badges, palettes), not theme colors
- LoRA base-model scan moved off the main thread — fixes a Windows "Not Responding" freeze on startup (main-thread wait 1.41s → 0.00s, list display 3.95s → 2.10s in measurement)
- Header, folder tree (two-column with right-aligned counts), cards (8px radius, 1:1.35 face, base-model pills), detail panel, and status bar restyled
- Prompt tags: click a tag chip to copy it; right-click for Edit / Copy / Search (search filters the card list); copy feedback is now an animated toast (4s)
- Assign an existing image as a thumbnail (right-click / Tools menu), resized to max 1024px, saved in the same `.preview.webp` format as generated thumbnails
- Multiple thumbnails per card (`.g2`, `.g3`, …), double-click flip animation, page pill (`2/3`), and delete-thumbnail-only actions by page via the Recycle Bin
- Wider cards: aspect ratio 2:3 → 1:1.35, implemented as cover-crop (top-weighted) rather than stretching, so faces are not distorted
- Fixed: case-insensitive Windows path comparison for thumbnails — a single thumbnail was being counted as two on all 7,575 cards with thumbnails

## v2.4 — 2026-10-14 — Favorites, Base-Model Badges, Folder Operations

- Favorites: star toggle on thumbnails, favorites node in the folder tree, persisted in `favorites.json`, the DB, and sidecar JSON
- LoRA base-model detection from `cm-info.json` and safetensors headers, with `ill` / `ani` / `mix` badges
- Base-model filter for the not-yet-created LoRA list, with colored base-model badges
- Folder create / rename / move from the folder tree (dialog + drag & drop), with name validation and entry-path rewriting
- LoRA sort mode persisted in `ui_state.json`

## v2.3 — 2026-07-11 — Move Dialog, Explorer Fix, Refactoring

- Move dialog folder tree unified with the main view; button order fixed
- Fixed Explorer launch for paths containing Japanese characters or spaces
- `main_window.py` split from 4,428 to 3,216 lines (`workers.py`, `widgets.py`, `settings_dialog.py` extracted)
- Logging introduced (`logging_setup.py`, rotating file handler); silent `except: pass` blocks replaced with debug logging
- Dependency version ranges pinned in `requirements.txt`

## v2.2 — 2026-07-07 — Selection & UI

- Shift+click rectangular range selection, Explorer-style
- Rename a card from the right-click menu (file name and DB entry stay in sync)
- Color-coded LoRA tags (`<lora:…>`, `<lyco:…>`)
- Tag delete mode with clearer visual state
- Bug fixes: scroll offset in range selection, selection anchor reset on model change, `.preview` suffix handling on rename

## v2.1 — 2026-06-26 — Windows Stability & Instant Thumbnail Refresh

- Fixed WinError 6 crashes with safe `Path.resolve()` wrappers
- Fixed handle leak in the file-manager launcher
- Thumbnails now refresh instantly after generation; race conditions and stale-cache overwrites fixed
- Cache keys changed to relative POSIX paths; generated-thumbnail cache protection (3s)
- LoRA matching by name set; "show all LoRAs" option in the uncreated-LoRA grid

## v2.0 — 2026-06-24 — Major Overhaul

Bug fixes, performance work, and architecture changes based on an external review.

- Fixed a critical context-menu bug that deleted the input field itself, numeric-parse crashes, API false positives on HTML responses, data loss on file overwrite, and path traversal outside the library
- Performance: O(1) thumbnail existence checks, single-pass library scan, SQLite WAL/PRAGMA tuning, background batch thumbnail generation, LRU content cache, SQL-side sorting
- Architecture: `main_window.py` split into `thumbnail_model.py`, `thumbnail_workers.py`, `tag_editor.py`, `new_wildcard_dialog.py`, and `ui_utils.py`; unique constraint on relative paths
- Features: random wildcard combination for thumbnail generation, ADetailer support, checkpoint list, live API generation status, dynamic tabs in the creation dialog
- Security: path validation after `resolve()`, safe overwrite via `shutil.move` / `copy2`
- Removed hardcoded personal paths from defaults

## v1.x — Initial Release

- Load, edit, and save wildcards; folder-tree filtering
- Search by file name, contents, custom tags, and LoRA name
- Thumbnail display and generation
- Copy / move import from `sd-dynamic-prompts` and `wildcard-gallery`
- Custom tags in sidecar `.wcm.json` files

Known issues in v1.x (all fixed in v2.0) included the context-menu deletion bug, crashes on invalid numeric input, API false positives, overwrite data-loss risk, path traversal, and slow thumbnail checks on large libraries.
