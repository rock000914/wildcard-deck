"""Internationalization (i18n) support for Wildcard Deck.

The UI source strings are authored in Japanese. Translation catalogs live in
``wildcard_manager/i18n/<code>.json`` and map the Japanese source text to the
target language. Nothing has to be changed at the call sites for static widget
texts: the installed application event filter translates any widget (and its
children) the moment it is shown, and :func:`retranslate_all` re-applies the
catalog when the user switches language at runtime.

Dynamic texts that are built with f-strings (status messages etc.) are only
translated when the complete string happens to be present in the catalog, which
is the intended, safe behaviour: unknown strings fall back to the original.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from PySide6.QtCore import QEvent, QObject
from PySide6.QtWidgets import (
    QAbstractButton,
    QApplication,
    QComboBox,
    QGroupBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QMenu,
    QPlainTextEdit,
    QTabWidget,
    QTableWidget,
    QTextEdit,
    QTreeWidget,
    QWidget,
)

log = logging.getLogger(__name__)

# code, native label
LANGUAGES: tuple[tuple[str, str], ...] = (
    ("ja", "日本語"),
    ("en", "English"),
    ("ko", "한국어"),
    ("zh", "中文（简体）"),
)
LANGUAGE_CODES: tuple[str, ...] = tuple(code for code, _ in LANGUAGES)
DEFAULT_LANGUAGE = "ja"

_CATALOG_DIR = Path(__file__).resolve().with_name("i18n")

_current_language = DEFAULT_LANGUAGE
_catalog: dict[str, str] = {}


def normalize_language(code: str | None) -> str:
    """Return a supported language code, falling back to the default."""
    value = (code or "").strip().lower()
    if value in LANGUAGE_CODES:
        return value
    # Accept regional variants such as en-US / zh-CN / ko-KR.
    base = value.split("-")[0].split("_")[0]
    if base in LANGUAGE_CODES:
        return base
    return DEFAULT_LANGUAGE


def available_languages() -> list[tuple[str, str]]:
    return list(LANGUAGES)


def language_label(code: str) -> str:
    for lang_code, label in LANGUAGES:
        if lang_code == code:
            return label
    return code


def current_language() -> str:
    return _current_language


def _load_catalog(code: str) -> dict[str, str]:
    if code == DEFAULT_LANGUAGE:
        return {}
    path = _CATALOG_DIR / f"{code}.json"
    if not path.exists():
        log.warning("Translation catalog not found: %s", path)
        return {}
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except Exception:
        log.exception("Failed to load translation catalog: %s", path)
        return {}
    return {str(k): str(v) for k, v in data.items() if str(v)}


def set_language(code: str) -> str:
    """Switch the active language and load its catalog."""
    global _current_language, _catalog
    _current_language = normalize_language(code)
    _catalog = _load_catalog(_current_language)
    log.info("UI language set to %s (%d entries)", _current_language, len(_catalog))
    return _current_language


def tr(text: str) -> str:
    """Translate one Japanese source string."""
    if not text or not _catalog:
        return text
    return _catalog.get(text, text)


# ---------------------------------------------------------------------------
# Widget translation
# ---------------------------------------------------------------------------

def _apply_string(obj, prop: str, getter, setter) -> None:
    """Translate ``obj``'s string, remembering the untranslated original.

    The original is stored as a Qt dynamic property so the text can be
    translated again (or restored to Japanese) later. If the text was changed
    by application code since the last pass, the new text becomes the new
    original, which keeps dynamically updated labels correct.
    """
    try:
        current = getter()
    except Exception:
        return
    if not isinstance(current, str) or not current:
        return

    source = obj.property(prop)
    last_applied = obj.property(f"{prop}_applied")
    source_translated = tr(source) if isinstance(source, str) else None
    if (
        not isinstance(source, str)
        or (current != source and current != source_translated and current != last_applied)
    ):
        obj.setProperty(prop, current)
        source = current

    translated = tr(source) or source
    obj.setProperty(f"{prop}_applied", translated)
    if translated != current:
        try:
            setter(translated)
        except Exception:
            log.debug("Failed to set translated text", exc_info=True)


def _apply_sequence(obj, prop: str, getter, count: int, setter) -> None:
    """Translate an indexed sequence (tab texts, combo items, list items)."""
    sources = obj.property(prop)
    sources = list(sources) if isinstance(sources, (list, tuple)) else []
    applied = obj.property(f"{prop}_applied")
    applied = list(applied) if isinstance(applied, (list, tuple)) else []

    if len(sources) > count:
        sources = sources[:count]
    for index in range(len(sources)):
        try:
            current = getter(index)
        except Exception:
            continue
        expected = tr(sources[index])
        last = applied[index] if index < len(applied) else None
        if current not in (sources[index], expected, last):
            sources[index] = current
    while len(sources) < count:
        try:
            sources.append(getter(len(sources)))
        except Exception:
            break
    obj.setProperty(prop, sources)

    applied = []
    for index, source in enumerate(sources):
        translated = tr(source) or source
        applied.append(translated)
        if not translated:
            continue
        try:
            if getter(index) != translated:
                setter(index, translated)
        except Exception:
            log.debug("Failed to translate sequence item", exc_info=True)
    obj.setProperty(f"{prop}_applied", applied)


def _apply_action(action) -> None:
    if action is None:
        return
    _apply_string(action, "i18n_action_text", action.text, action.setText)
    _apply_string(action, "i18n_action_tooltip", action.toolTip, action.setToolTip)
    _apply_string(action, "i18n_action_statustip", action.statusTip, action.setStatusTip)


def apply_widget(widget: QWidget) -> None:
    """Translate a single widget (not its children)."""
    if isinstance(widget, QWidget):
        _apply_string(widget, "i18n_window_title", widget.windowTitle, widget.setWindowTitle)
        _apply_string(widget, "i18n_tooltip", widget.toolTip, widget.setToolTip)
        _apply_string(widget, "i18n_statustip", widget.statusTip, widget.setStatusTip)
        _apply_string(widget, "i18n_whatsthis", widget.whatsThis, widget.setWhatsThis)
        for action in widget.actions():
            _apply_action(action)

    if isinstance(widget, QAbstractButton):
        _apply_string(widget, "i18n_text", widget.text, widget.setText)
    elif isinstance(widget, QLabel):
        _apply_string(widget, "i18n_text", widget.text, widget.setText)
    elif isinstance(widget, QGroupBox):
        _apply_string(widget, "i18n_title", widget.title, widget.setTitle)
    elif isinstance(widget, QMenu):
        _apply_string(widget, "i18n_menu_title", widget.title, widget.setTitle)

    if isinstance(widget, QLineEdit):
        _apply_string(widget, "i18n_placeholder", widget.placeholderText, widget.setPlaceholderText)
    elif isinstance(widget, QPlainTextEdit):
        _apply_string(widget, "i18n_placeholder", widget.placeholderText, widget.setPlaceholderText)
    elif isinstance(widget, QTextEdit):
        _apply_string(widget, "i18n_placeholder", widget.placeholderText, widget.setPlaceholderText)

    if isinstance(widget, QTabWidget):
        _apply_sequence(widget, "i18n_tab_texts", widget.tabText, widget.count(), widget.setTabText)

    if isinstance(widget, QComboBox):
        _apply_sequence(
            widget,
            "i18n_combo_items",
            lambda i: widget.itemText(i),
            widget.count(),
            lambda i, text: widget.setItemText(i, text),
        )

    if isinstance(widget, QListWidget):
        _apply_sequence(
            widget,
            "i18n_list_items",
            lambda i: widget.item(i).text(),
            widget.count(),
            lambda i, text: widget.item(i).setText(text),
        )

    if isinstance(widget, QTableWidget):
        _apply_sequence(
            widget,
            "i18n_h_headers",
            lambda i: widget.horizontalHeaderItem(i).text() if widget.horizontalHeaderItem(i) else "",
            widget.columnCount(),
            lambda i, text: widget.horizontalHeaderItem(i).setText(text) if widget.horizontalHeaderItem(i) else None,
        )
        _apply_sequence(
            widget,
            "i18n_v_headers",
            lambda i: widget.verticalHeaderItem(i).text() if widget.verticalHeaderItem(i) else "",
            widget.rowCount(),
            lambda i, text: widget.verticalHeaderItem(i).setText(text) if widget.verticalHeaderItem(i) else None,
        )

    if isinstance(widget, QTreeWidget):
        header = widget.headerItem()
        if header is not None:
            _apply_sequence(
                widget,
                "i18n_tree_headers",
                lambda i: header.text(i),
                header.columnCount(),
                lambda i, text: header.setText(i, text),
            )


def apply_tree(widget: QWidget) -> None:
    apply_widget(widget)
    for child in widget.findChildren(QWidget):
        apply_widget(child)


class _TranslationEventFilter(QObject):
    """Translate widgets as they are shown, so lazily built dialogs work."""

    def eventFilter(self, obj, event):  # noqa: N802 (Qt signature)
        if event.type() == QEvent.Show and isinstance(obj, QWidget):
            try:
                apply_tree(obj)
            except Exception:
                log.debug("Failed to translate shown widget", exc_info=True)
        return False


_event_filter: _TranslationEventFilter | None = None


def install(app: QApplication) -> None:
    """Install the show-time translator on the QApplication."""
    global _event_filter
    if _event_filter is not None:
        return
    _event_filter = _TranslationEventFilter(app)
    app.installEventFilter(_event_filter)


def retranslate_all(app: QApplication | None = None) -> None:
    """Re-apply the catalog to every existing widget."""
    app = app or QApplication.instance()
    if app is None:
        return
    for widget in app.allWidgets():
        try:
            apply_widget(widget)
        except Exception:
            log.debug("Failed to retranslate widget %r", widget, exc_info=True)
