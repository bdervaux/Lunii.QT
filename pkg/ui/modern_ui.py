"""
New, parent-friendly layout for Lunii.QT.

It is built ON TOP of the generated classic UI (pkg/ui/main_ui.py): every
widget, action and menu of the classic window is still created with the same
name, then moved into the new layout. This way pkg/main_window.py keeps all of
its features (import, export, hide, night mode, reorder, lost stories,
firmware, STUdio DB, logs...) and only the presentation changes.

Layout
  ┌──────────┬──────────────────────────────────────────────┐
  │ sidebar  │ page (stack)                                  │
  │  nav     │   Mes histoires | Ajouter | Ranger | Réparer  │
  │  device  │   (+ "Brancher la Lunii" when nothing found)  │
  │          ├──────────────────────────────────────────────┤
  │          │ progress card (only while a task runs)       │
  └──────────┴──────────────────────────────────────────────┘
"""
from PySide6.QtCore import Qt, QSize, QObject, QEvent, QByteArray, QCoreApplication, QRectF, Signal
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QFontDatabase
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (QAbstractButton, QButtonGroup, QCheckBox, QFrame, QGraphicsDropShadowEffect,
                               QGridLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget, QAbstractItemView,
                               QProgressBar, QPushButton, QStackedWidget, QVBoxLayout, QWidget, QScrollArea)

from pkg.ui.main_ui import Ui_MainWindow as _ClassicUi
from pkg.ui.theme import STYLESHEET, ACCENT



# --------------------------------------------------------------------------- icons
_SVG = {
    "book": '<path d="M4 19.5V5a2 2 0 0 1 2-2h14v15H6.5A2.5 2.5 0 0 0 4 20.5"/><path d="M20 18v3H6.5"/>',
    "plus": '<circle cx="12" cy="12" r="9"/><path d="M12 8v8M8 12h8"/>',
    "add": '<path d="M12 5v14M5 12h14"/>',
    "list": '<path d="M9 6h11M9 12h11M9 18h11"/><path d="M4 6h.01M4 12h.01M4 18h.01"/>',
    "kit": '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M12 10.5v6M9 13.5h6"/>',
    "help": '<circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 0 1 4.9.8c0 1.7-2.4 2.2-2.4 3.7"/><path d="M12 17h.01"/>',
    "refresh": '<path d="M20 11a8 8 0 1 0-2.3 5.7M20 4v7h-7"/>',
    "upload": '<path d="M12 16V4M7 9l5-5 5 5M5 20h14"/>',
    "download": '<path d="M12 4v11M7 10l5 5 5-5M5 20h14"/>',
    "trash": '<path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13"/>',
    "up": '<path d="M6 15l6-6 6 6"/>',
    "down": '<path d="M6 9l6 6 6-6"/>',
    "top": '<path d="M6 4h12M6 16l6-6 6 6"/><path d="M12 10v10"/>',
    "bottom": '<path d="M6 20h12M6 8l6 6 6-6"/><path d="M12 14V4"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/>',
    "folder": '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
    "log": '<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 8h8M8 12h8M8 16h5"/>',
    "chip": '<rect x="6" y="6" width="12" height="12" rx="2"/><path d="M9 2v4M15 2v4M9 18v4M15 18v4M2 9h4M2 15h4M18 9h4M18 15h4"/>',
    "image": '<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="9" cy="10" r="2"/><path d="M21 17l-5-5-9 8"/>',
    "broom": '<path d="M14 4l6 6M4 20l7-7M9 11l4 4-3 5-6-6z"/>',
    "audio": '<path d="M9 18V6l10-2v12"/><circle cx="6.5" cy="18" r="2.5"/><circle cx="16.5" cy="16" r="2.5"/>',
    "db": '<ellipse cx="12" cy="6" rx="7" ry="3"/><path d="M5 6v12c0 1.7 3.1 3 7 3s7-1.3 7-3V6M5 12c0 1.7 3.1 3 7 3s7-1.3 7-3"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/>',
    "usb": '<path d="M9 2v5M15 2v5M7 7h10v4a5 5 0 0 1-10 0zM12 16v6"/>',
    "moon": '<path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/>',
    "shelf": '<path d="M4 4h3v16H4zM9 4h3v16H9z"/><path d="M14.5 5.2l2.9-.8 3.6 14.6-2.9.8z"/>',
    "lunii": '<rect x="6" y="3" width="12" height="18" rx="4"/><circle cx="12" cy="10" r="3"/><path d="M9.5 17h5"/>',
    "send": '<path d="M4 12l16-8-6 16-2.5-6.5z"/><path d="M11.5 13.5L20 4"/>',
    "reveal": '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M12 10v6M9 13l3 3 3-3"/>',
    "eyeoff": ('<path d="M3 3l18 18"/><path d="M10.6 6.1A9.8 9.8 0 0 1 12 6c6 0 9.5 6 9.5 6a17 17 0 0 1-3 3.6'
               'M6.6 6.6A17 17 0 0 0 2.5 12S6 18 12 18a9.6 9.6 0 0 0 5.4-1.6"/>'),
}


def svg_icon(name: str, color: str = "#3B3760", size: int = 22, stroke: float = 2.0) -> QIcon:
    body = _SVG.get(name, "")
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" '
           f'stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round">{body}</svg>')
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    icon = QIcon()
    for scale in (1, 2):
        pix = QPixmap(size * scale, size * scale)
        pix.fill(Qt.transparent)
        painter = QPainter(pix)
        renderer.render(painter)
        painter.end()
        pix.setDevicePixelRatio(scale)
        icon.addPixmap(pix)
    return icon


# --------------------------------------------------------------------------- illustrations
SIGNATURE = "dervø"

# friendly crescent moon on an indigo tile (app logo)
LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="16" fill="#4C3FD1"/>
<circle cx="29" cy="35" r="19" fill="#FFD98A"/>
<circle cx="39" cy="26" r="16" fill="#4C3FD1"/>
<path d="M17 37 q3.5 3 7 0" stroke="#1E1B3A" stroke-width="2.4" fill="none" stroke-linecap="round"/>
<circle cx="18" cy="43.5" r="2.6" fill="#F7B7A3"/>
<path d="M49 13 l1.4 3.2 3.4.4 -2.6 2.3.8 3.4 -3-1.8 -3 1.8.8-3.4 -2.6-2.3 3.4-.4z" fill="#FFFFFF"/>
<circle cx="52" cy="35" r="1.8" fill="#FFFFFF" opacity=".85"/>
<circle cx="44" cy="47" r="1.3" fill="#FFFFFF" opacity=".7"/>
</svg>"""

# smiling Lunii-like box plugged into a laptop, under the stars
PLUG_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 200">
<ellipse cx="180" cy="178" rx="150" ry="14" fill="#ECEAFB"/>
<path d="M30 40 l2 5 5 .6 -3.8 3.4 1.1 5 -4.3-2.6 -4.3 2.6 1.1-5 -3.8-3.4 5-.6z" fill="#FFD98A"/>
<path d="M318 26 l1.6 4 4 .5 -3 2.7.9 4 -3.5-2.1 -3.5 2.1.9-4 -3-2.7 4-.5z" fill="#B8B1E8"/>
<circle cx="70" cy="22" r="3" fill="#B8B1E8"/><circle cx="290" cy="70" r="2.5" fill="#FFD98A"/>
<circle cx="160" cy="18" r="2" fill="#CFC6F5"/>
<rect x="44" y="56" width="92" height="112" rx="28" fill="#FFD98A" stroke="#1E1B3A" stroke-width="4"/>
<circle cx="90" cy="98" r="24" fill="#FFFFFF" stroke="#1E1B3A" stroke-width="4"/>
<path d="M80 96 q4 4 8 0 M92 96 q4 4 8 0" stroke="#1E1B3A" stroke-width="3" fill="none" stroke-linecap="round"/>
<path d="M83 106 q7 7 14 0" stroke="#1E1B3A" stroke-width="3" fill="none" stroke-linecap="round"/>
<circle cx="76" cy="105" r="3.5" fill="#F7B7A3"/><circle cx="104" cy="105" r="3.5" fill="#F7B7A3"/>
<rect x="70" y="140" width="40" height="6" rx="3" fill="#1E1B3A"/>
<path d="M136 120 C170 120 170 150 205 150" stroke="#4C3FD1" stroke-width="5" fill="none" stroke-dasharray="2 10" stroke-linecap="round"/>
<rect x="205" y="72" width="120" height="80" rx="10" fill="#FFFFFF" stroke="#1E1B3A" stroke-width="4"/>
<rect x="217" y="84" width="96" height="56" rx="5" fill="#ECEAFB"/>
<path d="M250 112 l9 9 17-19" stroke="#4C3FD1" stroke-width="6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M190 152 h150 l-12 14 h-126z" fill="#CFC6F5" stroke="#1E1B3A" stroke-width="4" stroke-linejoin="round"/>
</svg>"""

# a pile of books with a sleepy moon (empty library)
SHELF_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 170">
<ellipse cx="120" cy="156" rx="100" ry="10" fill="#ECEAFB"/>
<rect x="40" y="118" width="150" height="30" rx="8" fill="#A8D8F0" stroke="#1E1B3A" stroke-width="3.5"/>
<rect x="56" y="88" width="130" height="30" rx="8" fill="#F7B7A3" stroke="#1E1B3A" stroke-width="3.5"/>
<rect x="46" y="58" width="120" height="30" rx="8" fill="#B9E4C9" stroke="#1E1B3A" stroke-width="3.5"/>
<path d="M60 133 h70 M74 103 h60 M64 73 h50" stroke="#1E1B3A" stroke-width="3" stroke-linecap="round" opacity=".5"/>
<circle cx="190" cy="44" r="22" fill="#FFD98A"/><circle cx="200" cy="36" r="18" fill="#F6F5FB"/>
<path d="M176 46 q3 3 6 0" stroke="#1E1B3A" stroke-width="2.5" fill="none" stroke-linecap="round"/>
<path d="M120 20 l1.6 4 4 .5 -3 2.7.9 4 -3.5-2.1 -3.5 2.1.9-4 -3-2.7 4-.5z" fill="#B8B1E8"/>
<circle cx="150" cy="16" r="2.5" fill="#CFC6F5"/>
</svg>"""


def svg_pixmap(svg: str, width: int, height: int) -> QPixmap:
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    pix = QPixmap(width * 2, height * 2)
    pix.fill(Qt.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing)
    renderer.render(painter)
    painter.end()
    pix.setDevicePixelRatio(2)
    return pix


def logo_icon() -> QIcon:
    return QIcon(svg_pixmap(LOGO_SVG, 256, 256))


def _shadow(widget: QWidget, blur: int = 28, alpha: int = 28, dy: int = 6):
    effect = QGraphicsDropShadowEffect(widget)
    effect.setBlurRadius(blur)
    effect.setOffset(0, dy)
    effect.setColor(QColor(30, 27, 58, alpha))
    widget.setGraphicsEffect(effect)


def _centered(widget: QWidget) -> QHBoxLayout:
    """Centers a fixed-width widget without breaking word-wrapped labels inside it."""
    row = QHBoxLayout()
    row.addStretch(1)
    row.addWidget(widget)
    row.addStretch(1)
    return row


# --------------------------------------------------------------------------- small widgets
def _label(text: str, name: str = None, wrap: bool = False) -> QLabel:
    lbl = QLabel(text)
    if name:
        lbl.setObjectName(name)
    lbl.setWordWrap(wrap)
    return lbl


def _button(text: str, kind: str, icon: str = None, icon_color: str = None) -> QPushButton:
    btn = QPushButton(text)
    btn.setProperty("kind", kind)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setMinimumHeight(42)
    if icon:
        if icon_color is None:
            icon_color = "#FFFFFF" if kind == "primary" else ("#B42318" if kind == "danger" else ACCENT)
        btn.setIcon(svg_icon(icon, icon_color, 18, 2.2))
        btn.setIconSize(QSize(18, 18))
    return btn


def _reset_size(widget: QWidget):
    widget.setMinimumSize(0, 0)
    widget.setMaximumSize(16777215, 16777215)


class Switch(QAbstractButton):
    """iOS-like on/off switch."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(48, 28)

    def sizeHint(self):
        return QSize(48, 28)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        if not self.isEnabled():
            p.setOpacity(0.45)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(ACCENT) if self.isChecked() else QColor("#CFCBE3"))
        p.drawRoundedRect(QRectF(0, 0, 48, 28), 14, 14)
        p.setBrush(QColor("#FFFFFF"))
        x = 23 if self.isChecked() else 3
        p.drawEllipse(QRectF(x, 3, 22, 22))
        p.end()


class ToggleRow(QFrame):
    """Title + explanation on the left, a switch on the right. The whole row is clickable."""

    def __init__(self, icon: str, title: str, subtitle: str, parent=None):
        super().__init__(parent)
        self.setObjectName("toggleRow")
        self.setCursor(Qt.PointingHandCursor)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 12, 0, 12)
        lay.setSpacing(12)
        ico = QLabel()
        ico.setPixmap(svg_icon(icon, ACCENT, 22).pixmap(22, 22))
        ico.setAlignment(Qt.AlignTop)
        lay.addWidget(ico)
        texts = QVBoxLayout()
        texts.setSpacing(2)
        self.title_label = _label(title, "h3")
        self.subtitle_label = _label(subtitle, "small", wrap=True)
        texts.addWidget(self.title_label)
        texts.addWidget(self.subtitle_label)
        lay.addLayout(texts, 1)
        self.switch = Switch(self)
        lay.addWidget(self.switch, 0, Qt.AlignVCenter)

    def mouseReleaseEvent(self, event):
        if self.switch.isEnabled() and event.button() == Qt.LeftButton:
            self.switch.click()
        super().mouseReleaseEvent(event)


class DropZone(QFrame):
    """Big drag & drop target. Uses the main window's existing import logic."""
    clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dropZone")
        self.setAcceptDrops(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(220)
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignCenter)
        lay.setSpacing(10)
        ico = QLabel()
        ico.setPixmap(svg_icon("upload", ACCENT, 48, 1.8).pixmap(48, 48))
        ico.setAlignment(Qt.AlignCenter)
        lay.addWidget(ico)
        title = _label(QCoreApplication.translate("MainWindow", "Drop your stories here"), "h2")
        title.setAlignment(Qt.AlignCenter)
        lay.addWidget(title)
        sub = _label(QCoreApplication.translate("MainWindow", "or click to choose them on the computer"), "muted")
        sub.setAlignment(Qt.AlignCenter)
        lay.addWidget(sub)
        fmt = _label(QCoreApplication.translate("MainWindow", "Accepted: .zip, .7z, .pk (Lunii, Flam and STUdio packs)"), "small")
        fmt.setAlignment(Qt.AlignCenter)
        lay.addWidget(fmt)

    def _set_hover(self, on: bool):
        self.setProperty("hover", "true" if on else "false")
        self.style().unpolish(self)
        self.style().polish(self)

    def dragEnterEvent(self, event):
        win = self.window()
        if hasattr(win, "ts_dragenter_action"):
            win.ts_dragenter_action(event)
        self._set_hover(event.isAccepted())

    def dragMoveEvent(self, event):
        win = self.window()
        if hasattr(win, "ts_dragenter_action"):
            win.ts_dragenter_action(event)

    def dragLeaveEvent(self, event):
        self._set_hover(False)

    def dropEvent(self, event):
        self._set_hover(False)
        win = self.window()
        if hasattr(win, "ts_drop_action") and getattr(win, "audio_device", None):
            win.ts_drop_action(event)
            if hasattr(win, "show_page"):
                win.show_page("stories")

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(event)


class _VisibilityFollower(QObject):
    """Shows `target` only while at least one of `sources` is visible."""

    def __init__(self, target: QWidget, sources):
        super().__init__(target)
        self.target = target
        self.sources = list(sources)
        for src in self.sources:
            src.installEventFilter(self)
        self.update()

    def update(self):
        self.target.setVisible(any(not src.isHidden() for src in self.sources))

    def eventFilter(self, obj, event):
        if event.type() in (QEvent.Show, QEvent.Hide, QEvent.ShowToParent, QEvent.HideToParent):
            self.update()
        return False


def _page(title: str, subtitle: str):
    """Scrollable page with a title block. Returns (page widget, content layout)."""
    page = QWidget()
    page.setObjectName("page")
    outer = QVBoxLayout(page)
    outer.setContentsMargins(0, 0, 0, 0)
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    body = QWidget()
    body.setObjectName("page")
    lay = QVBoxLayout(body)
    lay.setContentsMargins(36, 30, 36, 30)
    lay.setSpacing(18)
    head = QVBoxLayout()
    head.setSpacing(4)
    head.addWidget(_label(title, "h1"))
    head.addWidget(_label(subtitle, "muted", wrap=True))
    lay.addLayout(head)
    scroll.setWidget(body)
    outer.addWidget(scroll)
    return page, lay


def _action_card(icon: str, title: str, text, button: QPushButton) -> QFrame:
    """text: a string, or a QLabel to keep updating it later."""
    card = QFrame()
    card.setObjectName("card")
    lay = QHBoxLayout(card)
    lay.setContentsMargins(20, 18, 20, 18)
    lay.setSpacing(16)
    ico = QLabel()
    ico.setPixmap(svg_icon(icon, ACCENT, 28, 1.8).pixmap(28, 28))
    ico.setAlignment(Qt.AlignTop)
    lay.addWidget(ico)
    texts = QVBoxLayout()
    texts.setSpacing(4)
    texts.addWidget(_label(title, "h3"))
    texts.addWidget(text if isinstance(text, QLabel) else _label(text, "muted", wrap=True))
    lay.addLayout(texts, 1)
    lay.addWidget(button, 0, Qt.AlignVCenter)
    return card


# --------------------------------------------------------------------------- the window
class Ui_ModernWindow(_ClassicUi):

    def setupUi(self, MainWindow):
        # 1. classic UI: creates every widget / action / menu the logic relies on
        super().setupUi(MainWindow)
        # 2. new presentation
        self._build_modern(MainWindow)
        self._retranslate_modern()

    # ------------------------------------------------------------------ build
    def _build_modern(self, MainWindow):
        classic = MainWindow.takeCentralWidget()      # keep it alive, it becomes the story column

        shell = QWidget()
        shell.setObjectName("shell")
        root = QHBoxLayout(shell)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_sidebar())

        right = QWidget()
        right.setObjectName("shell")
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(0, 0, 0, 0)
        right_lay.setSpacing(0)
        self.pages = QStackedWidget()
        self.pages.setObjectName("pages")
        right_lay.addWidget(self.pages, 1)
        right_lay.addWidget(self._build_progress_card())
        root.addWidget(right, 1)

        self.page_stories = self._build_stories_page(classic)
        self.page_library = self._build_library_page()
        self.page_add = self._build_add_page()
        self.page_order = self._build_order_page()
        self.page_repair = self._build_repair_page()
        self.page_connect = self._build_connect_page()
        self.pages_by_name = {
            "stories": self.page_stories,
            "add": self.page_add,
            "order": self.page_order,
            "repair": self.page_repair,
            "library": self.page_library,
            "connect": self.page_connect,
        }
        for page in self.pages_by_name.values():
            self.pages.addWidget(page)
        self.pages.setCurrentWidget(self.page_connect)

        MainWindow.setCentralWidget(shell)
        self.shell = shell
        MainWindow.resize(1200, 800)
        MainWindow.setMinimumSize(QSize(940, 620))
        MainWindow.setStyleSheet(STYLESHEET)
        MainWindow.setWindowIcon(logo_icon())

        # friendliest font available on this computer
        families = set(QFontDatabase.families())
        for family in ("Nunito", "Segoe UI", "SF Pro Text", ".AppleSystemUIFont", "Helvetica Neue",
                       "Ubuntu", "Cantarell", "Noto Sans", "Arial"):
            if family in families:
                MainWindow.setFont(QFont(family))
                break

    def _build_sidebar(self):
        side = QFrame()
        side.setObjectName("sidebar")
        side.setFixedWidth(248)
        lay = QVBoxLayout(side)
        lay.setContentsMargins(16, 22, 16, 16)
        lay.setSpacing(4)

        brand = QHBoxLayout()
        brand.setSpacing(12)
        logo = QLabel()
        logo.setPixmap(svg_pixmap(LOGO_SVG, 44, 44))
        brand.addWidget(logo)
        names = QVBoxLayout()
        names.setSpacing(0)
        names.addWidget(_label("Lunii.QT", "brand"))
        self.lbl_signature = _label("", "signature")
        names.addWidget(self.lbl_signature)
        brand.addLayout(names)
        brand.addStretch(1)
        lay.addLayout(brand)
        lay.addSpacing(22)

        self.nav_group = QButtonGroup(side)
        self.nav_group.setExclusive(True)

        def nav(icon, text):
            btn = QPushButton(text)
            btn.setObjectName("nav")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setIcon(svg_icon(icon, "#3B3760", 22))
            btn.setIconSize(QSize(22, 22))
            btn.setMinimumHeight(46)
            self.nav_group.addButton(btn)
            lay.addWidget(btn)
            return btn

        self.nav_stories = nav("lunii", "")
        self.nav_library = nav("shelf", "")
        self.nav_add = nav("plus", "")
        self.nav_order = nav("list", "")
        self.nav_repair = nav("kit", "")
        self.nav_stories.setChecked(True)

        lay.addStretch(1)

        # device selector (moved from the classic top bar)
        self.lbl_side_device = _label("", "sideCaption")
        lay.addWidget(self.lbl_side_device)
        dev_row = QHBoxLayout()
        dev_row.setSpacing(6)
        self.top_layout.removeWidget(self.combo_device)
        self.top_layout.removeWidget(self.btn_refresh)
        _reset_size(self.combo_device)
        self.combo_device.setMinimumHeight(38)
        dev_row.addWidget(self.combo_device, 1)
        _reset_size(self.btn_refresh)
        self.btn_refresh.setFixedSize(38, 38)
        self.btn_refresh.setFlat(False)
        self.btn_refresh.setProperty("kind", "ghost")
        self.btn_refresh.setIcon(svg_icon("refresh", "#3B3760", 20))
        self.btn_refresh.setIconSize(QSize(20, 20))
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        dev_row.addWidget(self.btn_refresh)
        lay.addLayout(dev_row)
        lay.addSpacing(10)

        self.nav_about = QPushButton("")
        self.nav_about.setObjectName("nav")
        self.nav_about.setCursor(Qt.PointingHandCursor)
        self.nav_about.setIcon(svg_icon("help", "#5E5A7A", 20))
        self.nav_about.setIconSize(QSize(20, 20))
        lay.addWidget(self.nav_about)
        return side

    def _build_progress_card(self):
        card = QFrame()
        card.setObjectName("progressCard")
        lay = QHBoxLayout(card)
        lay.setContentsMargins(28, 12, 28, 12)
        lay.setSpacing(16)

        # take the progress widgets out of their classic layouts
        self.totalLayout.removeWidget(self.lbl_total)
        self.totalLayout.removeWidget(self.pbar_total)
        self.storyLayout.removeWidget(self.lbl_story)
        self.verticalLayout.removeWidget(self.pbar_story)
        self.verticalLayout.removeWidget(self.pbar_file)
        self.prognstopLayout.removeWidget(self.btn_abort)

        bars = QGridLayout()
        bars.setHorizontalSpacing(12)
        bars.setVerticalSpacing(6)
        _reset_size(self.pbar_total)
        _reset_size(self.pbar_story)
        _reset_size(self.pbar_file)
        self.lbl_total.setObjectName("h3")
        self.lbl_story.setObjectName("small")
        bars.addWidget(self.lbl_total, 0, 0)
        bars.addWidget(self.pbar_total, 0, 1)
        bars.addWidget(self.lbl_story, 1, 0)
        bars.addWidget(self.pbar_story, 1, 1)
        bars.addWidget(self.pbar_file, 2, 1)
        bars.setColumnStretch(1, 1)
        lay.addLayout(bars, 1)

        _reset_size(self.btn_abort)
        self.btn_abort.setFlat(False)
        self.btn_abort.setProperty("kind", "danger")
        self.btn_abort.setMinimumHeight(40)
        self.btn_abort.setCursor(Qt.PointingHandCursor)
        lay.addWidget(self.btn_abort)

        self._progress_follower = _VisibilityFollower(card, [self.pbar_total, self.pbar_story, self.pbar_file])
        self.progress_card = card
        return card

    def _build_stories_page(self, classic: QWidget):
        page = QWidget()
        page.setObjectName("page")
        h = QHBoxLayout(page)
        h.setContentsMargins(36, 28, 28, 20)
        h.setSpacing(24)

        # ---- left column = the classic central widget, reorganised
        classic.setObjectName("page")
        v = self.verticalLayout_2
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(16)

        # leftovers of the classic top bar go elsewhere (sidebar / device card / repair page)
        for w in (self.btn_nightmode, self.btn_db):
            self.top_layout.removeWidget(w)
        self.top_layout.removeItem(self.horizontalSpacer)
        self.top_layout.setSpacing(10)
        self.le_filter.setMinimumHeight(40)
        self.le_filter.addAction(svg_icon("search", "#5E5A7A", 18), QLineEdit.ActionPosition.LeadingPosition)

        # header
        header = QHBoxLayout()
        titles = QVBoxLayout()
        titles.setSpacing(4)
        self.lbl_stories_title = _label("", "h1")
        self.lbl_stories_sub = _label("", "muted", wrap=True)
        titles.addWidget(self.lbl_stories_title)
        titles.addWidget(self.lbl_stories_sub)
        header.addLayout(titles, 1)
        self.btn_add_stories = _button("", "primary", "add")
        self.btn_add_stories.setMinimumHeight(46)
        header.addWidget(self.btn_add_stories, 0, Qt.AlignVCenter)
        v.insertLayout(0, header)

        v.insertWidget(1, self._build_device_card())

        # details (picture + description) move to the side panel
        self.details_layout.removeWidget(self.lbl_picture)
        self.details_layout.removeWidget(self.te_story_details)

        h.addWidget(classic, 1)
        h.addWidget(self._build_side_panel())
        return page

    def _build_device_card(self):
        card = QFrame()
        card.setObjectName("card")
        lay = QHBoxLayout(card)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(18)

        self.lbl_device_icon = QLabel()
        self.lbl_device_icon.setFixedSize(48, 48)
        lay.addWidget(self.lbl_device_icon)

        names = QVBoxLayout()
        names.setSpacing(2)
        self.lbl_device_name = _label("", "h3")
        self.lbl_device_state = _label("", "ok")
        names.addWidget(self.lbl_device_name)
        names.addWidget(self.lbl_device_state)
        lay.addLayout(names, 2)

        storage = QVBoxLayout()
        storage.setSpacing(6)
        self.lbl_storage_text = _label("", "small")
        self.bar_storage = QProgressBar()
        self.bar_storage.setObjectName("storage")
        self.bar_storage.setTextVisible(False)
        self.bar_storage.setRange(0, 1000)
        storage.addWidget(self.lbl_storage_text)
        storage.addWidget(self.bar_storage)
        lay.addLayout(storage, 3)

        count = QVBoxLayout()
        count.setSpacing(0)
        self.lbl_device_count = _label("0", "bigNumber")
        self.lbl_device_count.setAlignment(Qt.AlignCenter)
        self.lbl_device_count_caption = _label("", "small")
        self.lbl_device_count_caption.setAlignment(Qt.AlignCenter)
        count.addWidget(self.lbl_device_count)
        count.addWidget(self.lbl_device_count_caption)
        lay.addLayout(count)

        _reset_size(self.btn_nightmode)
        self.btn_nightmode.setFlat(False)
        self.btn_nightmode.setProperty("kind", "secondary")
        self.btn_nightmode.setIconSize(QSize(42, 20))
        self.btn_nightmode.setMinimumHeight(42)
        self.btn_nightmode.setCursor(Qt.PointingHandCursor)
        lay.addWidget(self.btn_nightmode, 0, Qt.AlignVCenter)
        self.device_card = card
        _shadow(card, 24, 18, 4)
        return card

    def _build_side_panel(self):
        panel = QFrame()
        panel.setObjectName("panel")
        panel.setFixedWidth(330)
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(22, 22, 22, 22)
        lay.setSpacing(10)

        # nothing selected
        self.panel_empty = QWidget()
        empty = QVBoxLayout(self.panel_empty)
        empty.setContentsMargins(0, 40, 0, 0)
        empty.setSpacing(10)
        ico = QLabel()
        ico.setPixmap(svg_icon("book", "#B8B1E8", 56, 1.6).pixmap(56, 56))
        ico.setAlignment(Qt.AlignCenter)
        empty.addWidget(ico)
        self.lbl_panel_empty = _label("", "muted", wrap=True)
        self.lbl_panel_empty.setAlignment(Qt.AlignCenter)
        empty.addWidget(self.lbl_panel_empty)
        empty.addStretch(1)
        lay.addWidget(self.panel_empty, 1)

        # one (or several) stories selected
        self.panel_story = QWidget()
        st = QVBoxLayout(self.panel_story)
        st.setContentsMargins(0, 0, 0, 0)
        st.setSpacing(10)

        _reset_size(self.lbl_picture)
        self.lbl_picture.setFixedSize(QSize(284, 220))
        self.lbl_picture.setAlignment(Qt.AlignCenter)
        st.addWidget(self.lbl_picture, 0, Qt.AlignHCenter)

        self.lbl_panel_title = _label("", "h2", wrap=True)
        self.lbl_panel_meta = _label("", "muted", wrap=True)
        st.addWidget(self.lbl_panel_title)
        st.addWidget(self.lbl_panel_meta)

        _reset_size(self.te_story_details)
        self.te_story_details.setMaximumHeight(110)
        self.te_story_details.setFrameShape(QFrame.NoFrame)
        st.addWidget(self.te_story_details)

        self.row_night = ToggleRow("moon", "", "")
        self.row_hidden = ToggleRow("eyeoff", "", "")
        st.addWidget(self.row_night)
        st.addWidget(self.row_hidden)

        self.btn_panel_export = _button("", "secondary", "download")
        st.addWidget(self.btn_panel_export)
        self.btn_panel_to_library = _button("", "secondary", "shelf")
        st.addWidget(self.btn_panel_to_library)
        self.panel_export_note = QFrame()
        self.panel_export_note.setObjectName("note")
        note_lay = QHBoxLayout(self.panel_export_note)
        note_lay.setContentsMargins(12, 10, 12, 10)
        self.lbl_panel_export_note = _label("", "small", wrap=True)
        note_lay.addWidget(self.lbl_panel_export_note)
        st.addWidget(self.panel_export_note)
        self.btn_panel_remove = _button("", "danger", "trash")
        st.addWidget(self.btn_panel_remove)
        st.addStretch(1)
        lay.addWidget(self.panel_story, 1)
        self.panel_story.setVisible(False)
        _shadow(panel, 30, 22, 6)
        return panel

    def _build_add_page(self):
        page, lay = _page(QCoreApplication.translate("MainWindow", "Add stories"), QCoreApplication.translate("MainWindow", "Your stories go straight onto the Lunii. Audio is converted automatically when needed."))
        self.drop_zone = DropZone()
        lay.addWidget(self.drop_zone)
        row = QHBoxLayout()
        self.btn_choose_files = _button(QCoreApplication.translate("MainWindow", "Choose files…"), "primary", "folder", "#FFFFFF")
        row.addWidget(self.btn_choose_files)
        row.addSpacing(16)
        self.chk_keep_copy = QCheckBox(QCoreApplication.translate("MainWindow", "Also keep a copy in my library"))
        self.chk_keep_copy.setChecked(True)
        self.chk_keep_copy.setCursor(Qt.PointingHandCursor)
        row.addWidget(self.chk_keep_copy)
        row.addStretch(1)
        lay.addLayout(row)

        self.btn_add_from_library = _button(QCoreApplication.translate("MainWindow", "Open my library"), "secondary", "shelf")
        lay.addWidget(_action_card("shelf", QCoreApplication.translate("MainWindow", "From my library"),
                                   QCoreApplication.translate("MainWindow", "Pick stories you already keep on the computer and send them to the Lunii."),
                                   self.btn_add_from_library))

        self.btn_ffmpeg = _button(QCoreApplication.translate("MainWindow", "Install"), "secondary", "download")
        self.lbl_ffmpeg_state = _label("", "muted", wrap=True)
        lay.addWidget(_action_card("audio", QCoreApplication.translate("MainWindow", "Audio converter (FFmpeg)"), self.lbl_ffmpeg_state, self.btn_ffmpeg))

        self.btn_import_studio_db = _button(QCoreApplication.translate("MainWindow", "Import…"), "secondary", "db")
        lay.addWidget(_action_card("db", QCoreApplication.translate("MainWindow", "STUdio story catalog"),
                                   QCoreApplication.translate("MainWindow", "Gives proper titles and descriptions to stories made with STUdio (unofficial.json)."),
                                   self.btn_import_studio_db))
        lay.addStretch(1)
        return page

    def _build_order_page(self):
        page, lay = _page(QCoreApplication.translate("MainWindow", "Arrange stories"),
                          QCoreApplication.translate("MainWindow", "This is the order in which your child discovers the stories with the wheel. Changes are saved on the Lunii right away."))
        row = QHBoxLayout()
        row.setSpacing(18)
        self.order_list = QListWidget()
        self.order_list.setObjectName("orderList")
        self.order_list.setIconSize(QSize(44, 44))
        self.order_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.order_list.setMinimumHeight(420)
        self.order_list.setUniformItemSizes(True)
        row.addWidget(self.order_list, 1)

        buttons = QVBoxLayout()
        buttons.setSpacing(10)
        self.btn_mv_top = _button(QCoreApplication.translate("MainWindow", "To the top"), "secondary", "top")
        self.btn_mv_up = _button(QCoreApplication.translate("MainWindow", "Move up"), "secondary", "up")
        self.btn_mv_down = _button(QCoreApplication.translate("MainWindow", "Move down"), "secondary", "down")
        self.btn_mv_bottom = _button(QCoreApplication.translate("MainWindow", "To the bottom"), "secondary", "bottom")
        for b in (self.btn_mv_top, self.btn_mv_up, self.btn_mv_down, self.btn_mv_bottom):
            b.setMinimumWidth(190)
            buttons.addWidget(b)
        tip = _label(QCoreApplication.translate("MainWindow", "Tip: select several stories with Ctrl or Shift to move them together."), "small", wrap=True)
        tip.setMaximumWidth(200)
        buttons.addSpacing(8)
        buttons.addWidget(tip)
        buttons.addStretch(1)
        row.addLayout(buttons)
        lay.addLayout(row, 1)
        return page

    def _build_repair_page(self):
        page, lay = _page(QCoreApplication.translate("MainWindow", "Repair and tools"), QCoreApplication.translate("MainWindow", "Everything you need when something goes wrong, or to keep a backup."))

        lay.addWidget(_label(QCoreApplication.translate("MainWindow", "Lost stories"), "h2"))
        self.btn_find_lost = _button(QCoreApplication.translate("MainWindow", "Search"), "secondary", "search")
        lay.addWidget(_action_card("search", QCoreApplication.translate("MainWindow", "Find lost stories"),
                                   QCoreApplication.translate("MainWindow", "Looks for stories still on the Lunii that your child can no longer play. Results show in the activity log."),
                                   self.btn_find_lost))
        self.btn_recover_lost = _button(QCoreApplication.translate("MainWindow", "Put back"), "primary", "refresh", "#FFFFFF")
        lay.addWidget(_action_card("refresh", QCoreApplication.translate("MainWindow", "Put them back"),
                                   QCoreApplication.translate("MainWindow", "Restores the lost stories that are in good condition."),
                                   self.btn_recover_lost))
        self.btn_clean_lost = _button(QCoreApplication.translate("MainWindow", "Clean up"), "danger", "broom")
        lay.addWidget(_action_card("broom", QCoreApplication.translate("MainWindow", "Delete what can't be saved"),
                                   QCoreApplication.translate("MainWindow", "Frees the space used by lost stories. This cannot be undone."),
                                   self.btn_clean_lost))

        lay.addSpacing(8)
        lay.addWidget(_label(QCoreApplication.translate("MainWindow", "Backups and updates"), "h2"))
        self.btn_export_all = _button(QCoreApplication.translate("MainWindow", "Back up…"), "secondary", "download")
        lay.addWidget(_action_card("download", QCoreApplication.translate("MainWindow", "Back up all my stories"),
                                   QCoreApplication.translate("MainWindow", "Copies every story that can be copied to a folder on the computer."),
                                   self.btn_export_all))
        # classic "refresh DB" button, its click is already wired to cb_db_refresh
        _reset_size(self.btn_db)
        self.btn_db.setFlat(False)
        self.btn_db.setProperty("kind", "secondary")
        self.btn_db.setIcon(svg_icon("image", ACCENT, 18, 2.2))
        self.btn_db.setIconSize(QSize(18, 18))
        self.btn_db.setMinimumHeight(42)
        self.btn_db.setCursor(Qt.PointingHandCursor)
        lay.addWidget(_action_card("image", QCoreApplication.translate("MainWindow", "Update covers and titles"),
                                   QCoreApplication.translate("MainWindow", "Downloads the latest official Lunii catalog again."),
                                   self.btn_db))
        self.btn_get_fw = _button(QCoreApplication.translate("MainWindow", "Download…"), "secondary", "chip")
        lay.addWidget(_action_card("chip", QCoreApplication.translate("MainWindow", "Keep a copy of the Lunii software"),
                                   QCoreApplication.translate("MainWindow", "Downloads the official firmware, to reinstall it if the Lunii breaks down. Requires your Lunii account."),
                                   self.btn_get_fw))
        self.btn_show_log = _button(QCoreApplication.translate("MainWindow", "Show"), "secondary", "log")
        lay.addWidget(_action_card("log", QCoreApplication.translate("MainWindow", "Activity log"),
                                   QCoreApplication.translate("MainWindow", "Technical details of everything Lunii.QT does. Useful when asking for help."),
                                   self.btn_show_log))
        lay.addStretch(1)
        return page

    def _build_connect_page(self):
        page = QWidget()
        page.setObjectName("page")
        lay = QVBoxLayout(page)
        lay.setContentsMargins(48, 40, 48, 40)
        lay.setSpacing(20)
        lay.addStretch(1)

        # why we landed here (e.g. "To add stories, plug in your Lunii first.")
        self.connect_reason = QFrame()
        self.connect_reason.setObjectName("reason")
        reason_lay = QHBoxLayout(self.connect_reason)
        reason_lay.setContentsMargins(18, 12, 18, 12)
        reason_ico = QLabel()
        reason_ico.setPixmap(svg_icon("info", "#7A4B00", 20).pixmap(20, 20))
        reason_lay.addWidget(reason_ico)
        self.lbl_connect_reason = _label("", "warn", wrap=True)
        reason_lay.addWidget(self.lbl_connect_reason, 1)
        self.connect_reason.setFixedWidth(560)
        self.connect_reason.setVisible(False)
        lay.addLayout(_centered(self.connect_reason))

        art = QLabel()
        art.setPixmap(svg_pixmap(PLUG_SVG, 360, 200))
        art.setAlignment(Qt.AlignCenter)
        lay.addWidget(art)

        title = _label(QCoreApplication.translate("MainWindow", "Plug in your Lunii"), "h1")
        title.setAlignment(Qt.AlignCenter)
        lay.addWidget(title)
        sub = _label(QCoreApplication.translate("MainWindow", "Lunii.QT finds it on its own a few seconds after it is plugged in. It also works with the Flam."), "muted", wrap=True)
        sub.setAlignment(Qt.AlignCenter)
        sub.setFixedWidth(560)
        lay.addLayout(_centered(sub))
        lib_row = QHBoxLayout()
        lib_row.addStretch(1)
        lib_row.addWidget(_label(QCoreApplication.translate("MainWindow", "No Lunii at hand?"), "small"))
        self.btn_connect_library = _button(QCoreApplication.translate("MainWindow", "Manage my library"), "link")
        self.btn_connect_library.setMinimumHeight(0)
        lib_row.addWidget(self.btn_connect_library)
        lib_row.addStretch(1)

        steps = QHBoxLayout()
        steps.setSpacing(16)
        for n, (head, text) in enumerate((
                (QCoreApplication.translate("MainWindow", "Plug the cable"), QCoreApplication.translate("MainWindow", "Connect the Lunii to the computer with its USB cable.")),
                (QCoreApplication.translate("MainWindow", "Turn the Lunii on"), QCoreApplication.translate("MainWindow", "Its screen shows the USB symbol: it is ready.")),
                (QCoreApplication.translate("MainWindow", "Wait a moment"), QCoreApplication.translate("MainWindow", "Your stories show up within a few seconds."))), start=1):
            card = QFrame()
            card.setObjectName("card")
            card.setFixedSize(236, 168)
            c = QVBoxLayout(card)
            c.setContentsMargins(20, 18, 20, 18)
            c.setSpacing(8)
            num = _label(str(n), "stepNumber")
            num.setAlignment(Qt.AlignCenter)
            c.addWidget(num)
            c.addWidget(_label(head, "h3"))
            body = _label(text, "muted", wrap=True)
            body.setFixedWidth(196)
            c.addWidget(body)
            c.addStretch(1)
            _shadow(card, 24, 16, 4)
            steps.addWidget(card)
        steps_box = QWidget()
        steps_box.setFixedWidth(3 * 236 + 2 * 16)
        steps_box.setLayout(steps)
        steps.setContentsMargins(0, 0, 0, 0)
        lay.addLayout(_centered(steps_box))

        btns = QHBoxLayout()
        btns.addStretch(1)
        self.btn_connect_retry = _button(QCoreApplication.translate("MainWindow", "Search again"), "primary", "refresh", "#FFFFFF")
        self.btn_connect_retry.setMinimumHeight(48)
        btns.addWidget(self.btn_connect_retry)
        btns.addStretch(1)
        lay.addLayout(btns)

        hint_row = QHBoxLayout()
        hint_row.addStretch(1)
        hint_row.addWidget(_label(QCoreApplication.translate("MainWindow", "Still nothing? Try another cable or USB port, or"), "small"))
        self.btn_connect_open = _button(QCoreApplication.translate("MainWindow", "open it manually…"), "link")
        self.btn_connect_open.setMinimumHeight(0)
        hint_row.addWidget(self.btn_connect_open)
        hint_row.addStretch(1)
        lay.addLayout(hint_row)
        lay.addLayout(lib_row)
        lay.addStretch(2)
        return page

    def _build_library_page(self):
        page = QWidget()
        page.setObjectName("page")
        h = QHBoxLayout(page)
        h.setContentsMargins(36, 28, 28, 20)
        h.setSpacing(24)

        col = QVBoxLayout()
        col.setSpacing(16)
        header = QHBoxLayout()
        titles = QVBoxLayout()
        titles.setSpacing(4)
        titles.addWidget(_label(QCoreApplication.translate("MainWindow", "My library"), "h1"))
        self.lbl_library_sub = _label("", "muted", wrap=True)
        titles.addWidget(self.lbl_library_sub)
        header.addLayout(titles, 1)
        self.btn_library_add = _button(QCoreApplication.translate("MainWindow", "Add to my library"), "primary", "add")
        self.btn_library_add.setMinimumHeight(46)
        header.addWidget(self.btn_library_add, 0, Qt.AlignVCenter)
        col.addLayout(header)

        tools = QHBoxLayout()
        tools.setSpacing(10)
        self.le_library_filter = QLineEdit()
        self.le_library_filter.setObjectName("le_filter")
        self.le_library_filter.setMinimumHeight(40)
        self.le_library_filter.setClearButtonEnabled(True)
        self.le_library_filter.addAction(svg_icon("search", "#5E5A7A", 18), QLineEdit.ActionPosition.LeadingPosition)
        tools.addWidget(self.le_library_filter, 1)
        self.btn_library_folder = _button(QCoreApplication.translate("MainWindow", "Open the folder"), "secondary", "folder")
        tools.addWidget(self.btn_library_folder)
        self.btn_library_change = _button(QCoreApplication.translate("MainWindow", "Change folder…"), "link")
        self.btn_library_change.setMinimumHeight(0)
        tools.addWidget(self.btn_library_change)
        col.addLayout(tools)

        self.library_stack = QStackedWidget()
        # empty library
        empty = QWidget()
        empty.setObjectName("page")
        e = QVBoxLayout(empty)
        e.setSpacing(14)
        e.addStretch(1)
        art = QLabel()
        art.setPixmap(svg_pixmap(SHELF_SVG, 240, 170))
        art.setAlignment(Qt.AlignCenter)
        e.addWidget(art)
        t = _label(QCoreApplication.translate("MainWindow", "Your library is empty"), "h2")
        t.setAlignment(Qt.AlignCenter)
        e.addWidget(t)
        sub = _label(QCoreApplication.translate("MainWindow", "Drop story files here (.zip, .7z, .pk), even without a Lunii. They will be ready to send whenever you want."), "muted", wrap=True)
        sub.setAlignment(Qt.AlignCenter)
        sub.setFixedWidth(520)
        e.addLayout(_centered(sub))
        e.addStretch(2)
        self.library_empty = empty
        self.library_stack.addWidget(empty)
        col.addWidget(self.library_stack, 1)
        h.addLayout(col, 1)

        # side panel
        panel = QFrame()
        panel.setObjectName("panel")
        panel.setFixedWidth(330)
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(22, 22, 22, 22)
        lay.setSpacing(10)
        self.library_panel_empty = QWidget()
        pe = QVBoxLayout(self.library_panel_empty)
        pe.setContentsMargins(0, 40, 0, 0)
        ico = QLabel()
        ico.setPixmap(svg_icon("shelf", "#B8B1E8", 56, 1.6).pixmap(56, 56))
        ico.setAlignment(Qt.AlignCenter)
        pe.addWidget(ico)
        self.lbl_library_panel_empty = _label("", "muted", wrap=True)
        self.lbl_library_panel_empty.setAlignment(Qt.AlignCenter)
        pe.addWidget(self.lbl_library_panel_empty)
        pe.addStretch(1)
        lay.addWidget(self.library_panel_empty, 1)

        self.library_panel_story = QWidget()
        ps = QVBoxLayout(self.library_panel_story)
        ps.setContentsMargins(0, 0, 0, 0)
        ps.setSpacing(10)
        self.lbl_library_cover = QLabel()
        self.lbl_library_cover.setObjectName("lbl_picture")
        self.lbl_library_cover.setFixedSize(QSize(284, 220))
        self.lbl_library_cover.setAlignment(Qt.AlignCenter)
        ps.addWidget(self.lbl_library_cover, 0, Qt.AlignHCenter)
        self.lbl_library_title = _label("", "h2", wrap=True)
        self.lbl_library_meta = _label("", "muted", wrap=True)
        self.lbl_library_desc = _label("", "small", wrap=True)
        self.lbl_library_desc.setMaximumHeight(90)
        ps.addWidget(self.lbl_library_title)
        ps.addWidget(self.lbl_library_meta)
        ps.addWidget(self.lbl_library_desc)
        self.btn_library_send = _button("", "primary", "send", "#FFFFFF")
        ps.addWidget(self.btn_library_send)
        self.library_send_note = QFrame()
        self.library_send_note.setObjectName("note")
        nl = QHBoxLayout(self.library_send_note)
        nl.setContentsMargins(12, 10, 12, 10)
        self.lbl_library_send_note = _label("", "small", wrap=True)
        nl.addWidget(self.lbl_library_send_note)
        ps.addWidget(self.library_send_note)
        self.btn_library_reveal = _button("", "secondary", "reveal")
        ps.addWidget(self.btn_library_reveal)
        self.btn_library_remove = _button("", "danger", "trash")
        ps.addWidget(self.btn_library_remove)
        ps.addStretch(1)
        lay.addWidget(self.library_panel_story, 1)
        self.library_panel_story.setVisible(False)
        _shadow(panel, 30, 22, 6)
        h.addWidget(panel)
        return page

    # ------------------------------------------------------------------ texts
    def _retranslate_modern(self):
        self.nav_stories.setText(QCoreApplication.translate("MainWindow", "My Lunii"))
        self.nav_library.setText(QCoreApplication.translate("MainWindow", "My library"))
        self.lbl_signature.setText(QCoreApplication.translate("MainWindow", "by {0}").format(SIGNATURE))
        self.btn_panel_to_library.setText(QCoreApplication.translate("MainWindow", "Copy to my library"))
        self.lbl_library_sub.setText(QCoreApplication.translate("MainWindow", "Stories kept on this computer. No Lunii needed to add or manage them."))
        self.le_library_filter.setPlaceholderText(QCoreApplication.translate("MainWindow", "Search my library"))
        self.lbl_library_panel_empty.setText(QCoreApplication.translate("MainWindow", "Click a story of your library to see it here."))
        self.btn_library_reveal.setText(QCoreApplication.translate("MainWindow", "Show in the folder"))
        self.btn_library_remove.setText(QCoreApplication.translate("MainWindow", "Remove from my library"))
        self.nav_add.setText(QCoreApplication.translate("MainWindow", "Add"))
        self.nav_order.setText(QCoreApplication.translate("MainWindow", "Arrange"))
        self.nav_repair.setText(QCoreApplication.translate("MainWindow", "Repair and tools"))
        self.nav_about.setText(QCoreApplication.translate("MainWindow", "About"))
        self.lbl_side_device.setText(QCoreApplication.translate("MainWindow", "PLUGGED-IN LUNII"))
        self.btn_refresh.setToolTip(QCoreApplication.translate("MainWindow", "Look for plugged-in Lunii again"))

        self.lbl_stories_title.setText(QCoreApplication.translate("MainWindow", "My stories"))
        self.lbl_stories_sub.setText(QCoreApplication.translate("MainWindow", "What is on the Lunii right now. Click a story to manage it."))
        self.btn_add_stories.setText(QCoreApplication.translate("MainWindow", "Add stories"))
        self.btn_nightmode.setText(QCoreApplication.translate("MainWindow", "Night mode"))
        self.btn_nightmode.setToolTip(QCoreApplication.translate("MainWindow", "Night mode settings of the Lunii"))
        self.lbl_device_count_caption.setText(QCoreApplication.translate("MainWindow", "stories"))

        self.lbl_panel_empty.setText(QCoreApplication.translate("MainWindow", "Click a story to see it here and change its settings."))
        self.row_night.title_label.setText(QCoreApplication.translate("MainWindow", "Night mode"))
        self.row_night.subtitle_label.setText(QCoreApplication.translate("MainWindow", "Plays on its own, softly, to fall asleep"))
        self.row_hidden.title_label.setText(QCoreApplication.translate("MainWindow", "Hide on the Lunii"))
        self.row_hidden.subtitle_label.setText(QCoreApplication.translate("MainWindow", "Stays on the Lunii, but your child no longer sees it"))
        self.btn_panel_export.setText(QCoreApplication.translate("MainWindow", "Save to the computer"))
        self.lbl_panel_export_note.setText(QCoreApplication.translate("MainWindow", "Official stories can't be copied to the computer. You can always get them back from your Lunii account."))
        self.btn_panel_remove.setText(QCoreApplication.translate("MainWindow", "Remove from the Lunii"))

        self.btn_db.setText(QCoreApplication.translate("MainWindow", "Update"))
        self.btn_abort.setText(QCoreApplication.translate("MainWindow", "Stop"))
