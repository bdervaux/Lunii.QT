"""
Cover wall ("Bibliothèque") view for Lunii.QT.

A QListWidget in icon mode showing every story of the device as a big cover
tile, the way a parent sees them on the Luniistore. Covers are filled in
asynchronously by pkg.api.covers.CoverFetcher; until then a pastel tile with the
story initials is shown.

Selection is kept in sync with the classic tree view by main_window, so every
existing action (export, hide, night mode, move, remove...) keeps working.
"""
import hashlib

from PySide6.QtCore import Qt, QSize, QRectF, Signal
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont, QPainterPath, QIcon
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QListView, QAbstractItemView

ROLE_UUID = Qt.UserRole + 1

TILE = 168          # cover size in px
RADIUS = 18

PASTELS = ["#FFD98A", "#A8D8F0", "#B9E4C9", "#F7B7A3", "#CFC6F5", "#FFE3B0", "#D9EBB0", "#F5C6DA"]
INK = QColor("#1E1B3A")
ACCENT = QColor("#4C3FD1")


def _pastel_for(uuid_str: str) -> QColor:
    h = int(hashlib.md5(uuid_str.encode()).hexdigest(), 16)
    return QColor(PASTELS[h % len(PASTELS)])


def _initials(title: str) -> str:
    words = [w for w in title.replace("-", " ").split() if w[:1].isalnum()]
    skip = {"le", "la", "les", "l", "un", "une", "des", "de", "du", "the", "a"}
    words = [w for w in words if w.lower().strip("'’") not in skip] or words
    return "".join(w[0] for w in words[:2]).upper() or "?"


def _rounded(pix: QPixmap) -> QPixmap:
    out = QPixmap(TILE, TILE)
    out.fill(Qt.transparent)
    p = QPainter(out)
    p.setRenderHint(QPainter.Antialiasing)
    path = QPainterPath()
    path.addRoundedRect(QRectF(0, 0, TILE, TILE), RADIUS, RADIUS)
    p.setClipPath(path)
    p.drawPixmap(0, 0, pix)
    p.end()
    return out


def _placeholder(uuid_str: str, title: str) -> QPixmap:
    pix = QPixmap(TILE, TILE)
    pix.fill(_pastel_for(uuid_str))
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    f = QFont()
    f.setPointSize(34)
    f.setBold(True)
    p.setFont(f)
    p.setPen(INK)
    p.drawText(pix.rect(), Qt.AlignCenter, _initials(title))
    p.end()
    return _rounded(pix)


def _cover_from_bytes(data: bytes):
    src = QPixmap()
    if not data or not src.loadFromData(data):
        return None
    # centre-crop to a square, then scale
    side = min(src.width(), src.height())
    src = src.copy((src.width() - side) // 2, (src.height() - side) // 2, side, side)
    src = src.scaled(TILE, TILE, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
    return _rounded(src)


def _badge_font() -> QFont:
    f = QFont()
    f.setPointSize(9)
    f.setBold(True)
    return f


def _badge_width(p: QPainter, text: str) -> int:
    p.setFont(_badge_font())
    return p.fontMetrics().horizontalAdvance(text) + 16


def _badge(p: QPainter, x: int, y: int, text: str, bg: QColor, fg: QColor):
    w = _badge_width(p, text)
    rect = QRectF(x, y, w, 22)
    p.setPen(Qt.NoPen)
    p.setBrush(bg)
    p.drawRoundedRect(rect, 11, 11)
    p.setPen(fg)
    p.drawText(rect, Qt.AlignCenter, text)
    return w


def decorate(cover: QPixmap, position: int, night: bool, hidden: bool, official: bool,
             night_label: str, hidden_label: str, perso_label: str) -> QPixmap:
    pix = QPixmap(cover)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)

    # hidden: light veil first, badges stay readable on top
    if hidden:
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(246, 245, 251, 160))
        p.drawRoundedRect(QRectF(0, 0, TILE, TILE), RADIUS, RADIUS)

    # position on the device (order in which the child discovers it)
    _badge(p, 8, 8, str(position), QColor("#FFFFFF"), INK)
    # night mode
    if night:
        _badge(p, TILE - 8 - _badge_width(p, night_label), 8, night_label, INK, QColor("#FFFFFF"))
    # third-party story
    if not official:
        _badge(p, 8, TILE - 30, perso_label, QColor("#FFFFFF"), ACCENT)
    if hidden:
        _badge(p, (TILE - _badge_width(p, hidden_label)) // 2, TILE // 2 - 11, hidden_label,
               QColor("#ECEAFB"), QColor("#3B3760"))
    p.end()
    return pix


class LibraryView(QListWidget):
    """Big-cover grid of the device stories."""

    # emitted with the list of selected story uuids (upper-case strings)
    signal_selection = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("library_view")
        self.setViewMode(QListView.IconMode)
        self.setResizeMode(QListView.Adjust)
        self.setMovement(QListView.Static)
        self.setWrapping(True)
        self.setWordWrap(True)
        self.setUniformItemSizes(True)
        self.setIconSize(QSize(TILE, TILE))
        self.setGridSize(QSize(TILE + 32, TILE + 64))
        self.setSpacing(6)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DropOnly)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setStyleSheet(
            "QListWidget#library_view { background: #F6F5FB; border: none; padding: 12px; }"
            "QListWidget#library_view::item { border-radius: 14px; padding: 6px; color: #1E1B3A; }"
            "QListWidget#library_view::item:hover { background: #ECEAFB; }"
            "QListWidget#library_view::item:selected { background: #DCD7FA; color: #1E1B3A; }"
        )
        self._items = {}    # uuid -> QListWidgetItem
        self._meta = {}     # uuid -> dict(position, night, hidden, official, title)
        self._covers = {}   # uuid -> QPixmap (raw rounded cover, before badges)
        self._labels = ("Nuit", "Masquée", "Perso")
        self.itemSelectionChanged.connect(self._emit_selection)

    def set_labels(self, night: str, hidden: str, perso: str):
        self._labels = (night, hidden, perso)

    # ---------- content ----------
    def populate(self, stories_with_pos, tooltip_fn=None):
        """stories_with_pos: iterable of (position, story)"""
        self.blockSignals(True)
        self.clear()
        self._items.clear()
        self._meta.clear()
        for position, story in stories_with_pos:
            uuid = story.str_uuid
            meta = dict(position=position, night=bool(story.night_mode()), hidden=bool(story.hidden),
                        official=bool(story.is_official()), title=story.name)
            self._meta[uuid] = meta
            item = QListWidgetItem(story.name)
            item.setData(ROLE_UUID, uuid)
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignTop)
            item.setSizeHint(QSize(TILE + 28, TILE + 58))
            if tooltip_fn:
                item.setToolTip(tooltip_fn(story))
            self.addItem(item)
            self._items[uuid] = item
            self._refresh_icon(uuid)
        self.blockSignals(False)

    def set_cover(self, uuid: str, data: bytes):
        cover = _cover_from_bytes(data)
        if cover is None:
            return
        self._covers[uuid] = cover
        if uuid in self._items:
            self._refresh_icon(uuid)

    def _refresh_icon(self, uuid: str):
        meta = self._meta[uuid]
        base = self._covers.get(uuid) or _placeholder(uuid, meta["title"])
        pix = decorate(base, meta["position"], meta["night"], meta["hidden"], meta["official"], *self._labels)
        self._items[uuid].setIcon(QIcon(pix))

    def has_cover(self, uuid: str) -> bool:
        return uuid in self._covers

    def cover_icon(self, uuid: str, size: int = 40):
        """Small cover for the classic list (None if not downloaded yet)."""
        cover = self._covers.get(uuid)
        if cover is None:
            return None
        return QIcon(cover.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    # ---------- selection ----------
    def selected_uuids(self):
        return [it.data(ROLE_UUID) for it in self.selectedItems()]

    def select_uuids(self, uuids):
        self.blockSignals(True)
        self.clearSelection()
        first = None
        for uuid in uuids:
            item = self._items.get(uuid)
            if item:
                item.setSelected(True)
                first = first or item
        if first:
            self.scrollToItem(first)
        self.blockSignals(False)

    def _emit_selection(self):
        self.signal_selection.emit(self.selected_uuids())
