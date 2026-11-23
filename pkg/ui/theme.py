"""
"Veilleuse" theme for Lunii.QT: soft, rounded, high-contrast enough for everyone.

Colors
  ground  #F6F5FB   surface #FFFFFF   line #E6E3F3
  ink     #1E1B3A   muted   #5E5A7A   accent #4C3FD1 (indigo)
"""

INK = "#1E1B3A"
MUTED = "#5E5A7A"
ACCENT = "#4C3FD1"
GROUND = "#F6F5FB"
DANGER = "#B42318"

FONT_STACK = '"Nunito", "Segoe UI", "SF Pro Text", "Helvetica Neue", "Ubuntu", Arial, sans-serif'

STYLESHEET = f"""
QMainWindow, QWidget#shell, QStackedWidget#pages, QWidget#page {{
    background: {GROUND};
}}
QWidget {{
    font-size: 14px;
    color: {INK};
}}

/* ---------- sidebar ---------- */
QFrame#sidebar {{
    background: #FFFFFF;
    border: none;
    border-right: 1px solid #E6E3F3;
}}
QLabel#brand {{ font-size: 21px; font-weight: 800; }}
QLabel#sideCaption {{ color: {MUTED}; font-size: 12px; font-weight: 800; }}
QPushButton#nav {{
    text-align: left;
    padding: 11px 14px;
    border: none;
    border-radius: 12px;
    font-size: 15px;
    font-weight: 700;
    color: #3B3760;
    background: transparent;
}}
QPushButton#nav:hover {{ background: #F3F1FD; }}
QPushButton#nav:checked {{ background: #ECEAFB; color: {ACCENT}; font-weight: 800; }}

/* ---------- text ---------- */
QLabel#h1 {{ font-size: 28px; font-weight: 800; }}
QLabel#h2 {{ font-size: 19px; font-weight: 800; }}
QLabel#h3 {{ font-size: 15px; font-weight: 800; }}
QLabel#muted {{ color: {MUTED}; }}
QLabel#small {{ color: {MUTED}; font-size: 12px; }}
QLabel#bigNumber {{ font-size: 30px; font-weight: 800; color: {ACCENT}; }}
QLabel#stepNumber {{
    background: {ACCENT}; color: #FFFFFF; border-radius: 17px;
    font-size: 16px; font-weight: 800;
    min-width: 34px; max-width: 34px; min-height: 34px; max-height: 34px;
}}
QLabel#ok {{ color: #1F6B45; font-weight: 800; }}
QLabel#warn {{ color: #7A4B00; font-weight: 800; }}

/* ---------- cards ---------- */
QFrame#card, QFrame#panel {{
    background: #FFFFFF;
    border: 1px solid #E6E3F3;
    border-radius: 18px;
}}
QFrame#card QLabel, QFrame#panel QLabel, QFrame#toggleRow QLabel {{ background: transparent; border: none; }}
QFrame#toggleRow {{ background: transparent; border: none; border-top: 1px solid #EFEDF7; }}
QFrame#note {{ background: {GROUND}; border: none; border-radius: 12px; }}
QFrame#reason {{ background: #FFF1D6; border: none; border-radius: 14px; }}
QFrame#reason QLabel {{ background: transparent; }}

/* ---------- buttons ---------- */
QPushButton, QToolButton {{
    border-radius: 19px;
    padding: 9px 18px;
    font-weight: 800;
    font-size: 14px;
}}
QPushButton[kind="primary"] {{ background: {ACCENT}; color: #FFFFFF; border: none; }}
QPushButton[kind="primary"]:hover {{ background: #3F33B8; }}
QPushButton[kind="primary"]:disabled {{ background: #B8B1E8; }}
QPushButton[kind="secondary"], QToolButton#btn_view {{
    background: #FFFFFF; color: {ACCENT}; border: 2px solid {ACCENT};
}}
QPushButton[kind="secondary"]:hover, QToolButton#btn_view:hover {{ background: #F3F1FD; }}
QPushButton[kind="secondary"]:disabled {{ color: #A9A4C4; border-color: #DCD8EE; }}
QPushButton[kind="danger"] {{ background: transparent; color: {DANGER}; border: none; }}
QPushButton[kind="danger"]:hover {{ background: #FDE7E5; }}
QPushButton[kind="danger"]:disabled {{ color: #D9B3AF; }}
QPushButton[kind="link"] {{ background: transparent; color: {ACCENT}; border: none; padding: 4px 6px; text-decoration: underline; }}
QPushButton[kind="ghost"] {{ background: transparent; color: #3B3760; border: none; border-radius: 12px; padding: 8px 10px; }}
QPushButton[kind="ghost"]:hover {{ background: #F3F1FD; }}

/* ---------- inputs ---------- */
QLineEdit#le_filter {{
    background: #FFFFFF; border: 1px solid #DCD8EE; border-radius: 19px;
    padding: 8px 16px; font-size: 14px;
}}
QLineEdit#le_filter:focus {{ border: 2px solid {ACCENT}; }}
QComboBox {{
    background: {GROUND}; border: 1px solid #DCD8EE; border-radius: 12px;
    padding: 7px 10px; font-weight: 700;
}}
QComboBox QAbstractItemView {{ background: #FFFFFF; selection-background-color: #ECEAFB; selection-color: {INK}; }}

/* ---------- progress ---------- */
QProgressBar {{
    background: #ECEAFB; border: none; border-radius: 5px;
    min-height: 10px; max-height: 10px; color: transparent;
}}
QProgressBar::chunk {{ background: {ACCENT}; border-radius: 5px; }}
QProgressBar#storage {{ min-height: 14px; max-height: 14px; border-radius: 7px; }}
QProgressBar#storage::chunk {{ border-radius: 7px; }}
QProgressBar#storage[low="true"]::chunk {{ background: {DANGER}; }}
QProgressBar#pbar_file {{ min-height: 5px; max-height: 5px; }}
QFrame#progressCard {{ background: #FFFFFF; border: none; border-top: 1px solid #E6E3F3; }}

/* ---------- lists ---------- */
QListWidget#orderList {{
    background: #FFFFFF; border: 1px solid #E6E3F3; border-radius: 18px; padding: 8px;
    font-size: 15px; font-weight: 700;
}}
QListWidget#orderList::item {{ padding: 8px; border-radius: 12px; }}
QListWidget#orderList::item:hover {{ background: #F3F1FD; }}
QListWidget#orderList::item:selected {{ background: #DCD7FA; color: {INK}; }}
QTreeWidget {{ background: #FFFFFF; border: 1px solid #E6E3F3; border-radius: 14px; }}
QTextBrowser#te_story_details {{ border: none; background: transparent; color: #3B3760; font-size: 13px; }}
QLabel#lbl_picture {{ background: {GROUND}; border-radius: 16px; color: {MUTED}; }}

/* ---------- drop zone ---------- */
QFrame#dropZone {{ background: #FBFAFF; border: 2px dashed #B8B1E8; border-radius: 22px; }}
QFrame#dropZone[hover="true"] {{ background: #ECEAFB; border: 2px dashed {ACCENT}; }}
QFrame#dropZone QLabel {{ background: transparent; border: none; }}

/* ---------- chrome ---------- */
QStatusBar {{ background: #FFFFFF; color: {MUTED}; border-top: 1px solid #E6E3F3; }}
QStatusBar QLabel {{ color: {MUTED}; }}
QMenuBar {{ background: #FFFFFF; border-bottom: 1px solid #E6E3F3; }}
QMenuBar::item {{ padding: 6px 12px; background: transparent; }}
QMenuBar::item:selected {{ background: #ECEAFB; border-radius: 8px; }}
QMenu {{ background: #FFFFFF; border: 1px solid #E6E3F3; padding: 6px; }}
QMenu::item {{ padding: 7px 24px 7px 12px; border-radius: 8px; }}
QMenu::item:selected {{ background: #ECEAFB; color: {INK}; }}
QToolTip {{ background: {INK}; color: #FFFFFF; border: none; padding: 6px 8px; border-radius: 6px; }}
QScrollBar:vertical {{ background: transparent; width: 10px; margin: 4px; }}
QScrollBar::handle:vertical {{ background: #D5D1EC; border-radius: 4px; min-height: 30px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
"""
