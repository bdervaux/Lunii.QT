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

    # MYLUNII_SELFTEST=<file>: build checks (opens the window, writes "ok" or the error, quits)
    selftest = os.environ.get("MYLUNII_SELFTEST")
    if selftest:
        import traceback
        from PySide6.QtCore import QTimer

        def report(text):
            with open(selftest, "w", encoding="utf-8") as fp:
                fp.write(text)

        def hook(exc_type, exc, tb):
            report("ERROR\n" + "".join(traceback.format_exception(exc_type, exc, tb)))
            os._exit(1)
        sys.excepthook = hook
        try:
            window = MainWindow(app)
            window.show()
            for page in ("library", "add", "order", "repair", "stories"):
                window.show_page(page)
        except Exception:
            hook(*sys.exc_info())

        def finish():
            report(f"ok\npages={len(window.pages_by_name)}\ntitle={window.windowTitle()}\n")
            window.close()
            app.quit()
        QTimer.singleShot(6000, finish)
        sys.exit(app.exec())

    window = MainWindow(app)
    window.show()

    sys.exit(app.exec())
