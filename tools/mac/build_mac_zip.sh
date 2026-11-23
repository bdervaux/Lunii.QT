#!/bin/bash
# Builds dist/MyLunii-Mac.zip:
#   MyLunii-Mac/
#     MyLunii.app                  self-contained app (program in Contents/Resources/app)
#     Installer MyLunii.command    double-click installer
#     installer-mylunii.sh         same installer for the Terminal
#     LISEZ-MOI.txt
#
# Needs pyside6-lrelease and pyside6-rcc (pip install PySide6-Essentials), or set PYSIDE_BIN.
# Works on macOS (ditto) and Linux (zip).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT="$ROOT/dist"
STAGE="$(mktemp -d)/MyLunii-Mac"
BIN="${PYSIDE_BIN:-}"
tool() { if [ -n "$BIN" ]; then echo "$BIN/$1"; else command -v "$1"; fi; }

echo "▶ Translations and resources"
"$(tool pyside6-lrelease)" "$ROOT/locales/fr_FR.ts" -qm "$ROOT/locales/fr_FR.qm"
(cd "$ROOT" && "$(tool pyside6-rcc)" resources.qrc -o resources_rc.py)

echo "▶ App bundle"
mkdir -p "$STAGE"
cp -R "$ROOT/MyLunii.app" "$STAGE/"
APP_RES="$STAGE/MyLunii.app/Contents/Resources/app"
mkdir -p "$APP_RES"
cp "$ROOT/lunii-qt.py" "$ROOT/resources_rc.py" "$ROOT/requirements-launcher.txt" "$ROOT/LICENSE" "$APP_RES/"
mkdir -p "$APP_RES/locales"
cp "$ROOT/locales/"*.qm "$APP_RES/locales/" 2>/dev/null || true
(cd "$ROOT" && tar --exclude='__pycache__' --exclude='*.pyc' -cf - pkg) | (cd "$APP_RES" && tar -xf -)
cp "$ROOT/res/mylunii.icns" "$STAGE/MyLunii.app/Contents/Resources/AppIcon.icns"
chmod +x "$STAGE/MyLunii.app/Contents/MacOS/MyLunii"

echo "▶ Installers"
cp "$ROOT/tools/mac/Installer MyLunii.command" "$ROOT/tools/mac/installer-mylunii.sh" "$ROOT/tools/mac/LISEZ-MOI.txt" "$STAGE/"
chmod +x "$STAGE/Installer MyLunii.command" "$STAGE/installer-mylunii.sh"

echo "▶ Permissions"
chmod -R u+rwX,go+rX "$STAGE"
chmod +x "$STAGE/MyLunii.app/Contents/MacOS/MyLunii" "$STAGE/Installer MyLunii.command" "$STAGE/installer-mylunii.sh"

echo "▶ Zip"
mkdir -p "$OUT"
rm -f "$OUT/MyLunii-Mac.zip"
if command -v ditto >/dev/null 2>&1; then
  xattr -cr "$STAGE" 2>/dev/null || true
  ditto -c -k --sequesterRsrc --keepParent "$STAGE" "$OUT/MyLunii-Mac.zip"
else
  (cd "$(dirname "$STAGE")" && zip -qry "$OUT/MyLunii-Mac.zip" "MyLunii-Mac")
fi
rm -rf "$(dirname "$STAGE")"
echo "✔ $OUT/MyLunii-Mac.zip ($(du -h "$OUT/MyLunii-Mac.zip" | cut -f1))"
