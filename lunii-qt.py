import os
import subprocess
import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTranslator, QLocale, Qt

from pkg.main_window import MainWindow


if __name__ == "__main__":
    app = QApplication([])
    app.setStyle("Fusion")   # Fusion renders the "Veilleuse" stylesheet the same on Windows, macOS and Linux
    app.setAttribute(Qt.AA_DontShowIconsInMenus, False)

    translator = QTranslator(app)
    path = ':/translations/locales'
    # user languages, best first: macOS preferences, LANG, then Qt's view
    # (recent Qt only reports the languages an app bundle declares)
    languages = []
    if sys.platform == "darwin":
        try:
            out = subprocess.run(["defaults", "read", "-g", "AppleLanguages"],
                                 capture_output=True, text=True, timeout=3).stdout
            languages += [l.strip().strip('",()') for l in out.splitlines() if l.strip().strip('",()')]
        except Exception:
            pass
    languages += [os.environ.get("LANG", "").split(".")[0]]
    languages += [QLocale.system().name()] + list(QLocale.system().uiLanguages())
    languages = [l for l in languages if l]
    for language in languages:
        if language.lower().startswith("fr") and translator.load(f"{path}/fr_FR.qm"):
            app.installTranslator(translator)
            break
        if language.lower().startswith("en"):
            break

    window = MainWindow(app)
    window.show()

    sys.exit(app.exec())
