#!/bin/bash
# Installe MyLunii sur ce Mac :
#   1. débloque l'application (macOS bloque ce qui vient d'Internet sans signature Apple),
#   2. installe Python si besoin (installateur officiel python.org, le mot de passe du Mac est demandé),
#   3. copie MyLunii.app dans Applications,
#   4. prépare l'application (2 à 5 minutes la première fois) et l'ouvre.
#
# Dans le Terminal :   bash "chemin/vers/installer-mylunii.sh"
# (astuce : tapez « bash » puis une espace, glissez ce fichier dans la fenêtre du Terminal, puis Entrée)

set -u

main() {
  HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  APP_SRC="$HERE/MyLunii.app"
  export PATH="/Library/Frameworks/Python.framework/Versions/Current/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"

  say()  { printf "\n\033[1;35m▶ %s\033[0m\n" "$1"; }
  fail() { printf "\n\033[1;31m✖ %s\033[0m\n\n" "$1"; exit 1; }

  [ -d "$APP_SRC" ] || fail "MyLunii.app est introuvable : gardez ce script dans le même dossier que l'application."

  # 1. déblocage
  say "Déblocage de MyLunii (sécurité macOS)…"
  xattr -dr com.apple.quarantine "$HERE" 2>/dev/null
  chmod +x "$APP_SRC/Contents/MacOS/MyLunii" "$HERE"/*.command "$HERE"/*.sh 2>/dev/null

  # 2. Python
  say "Recherche de Python…"
  PY=""
  for candidate in python3.12 python3.13 python3.11 python3.10 python3; do
    path="$(command -v "$candidate" 2>/dev/null)" || continue
    [ -z "$path" ] && continue
    if [ "$path" = "/usr/bin/python3" ] && ! xcode-select -p >/dev/null 2>&1; then
      continue
    fi
    if "$path" -c "import sys; sys.exit(0 if (3, 9) <= sys.version_info[:2] <= (3, 13) else 1)" >/dev/null 2>&1; then
      PY="$path"; break
    fi
  done

  if [ -z "$PY" ]; then
    say "Python n'est pas installé : téléchargement de l'installateur officiel (python.org)…"
    PKG_URL=""
    for n in $(seq 30 -1 5); do
      url="https://www.python.org/ftp/python/3.13.$n/python-3.13.$n-macos11.pkg"
      if curl -fsIL "$url" >/dev/null 2>&1; then PKG_URL="$url"; break; fi
    done
    [ -n "$PKG_URL" ] || { open "https://www.python.org/downloads/macos/"; fail "Impossible de trouver l'installateur Python. Installez Python 3.13 depuis la page qui vient de s'ouvrir, puis relancez ce script."; }
    PKG="$(mktemp -d)/python.pkg"
    curl -fL --progress-bar "$PKG_URL" -o "$PKG" || fail "Téléchargement de Python impossible. Vérifiez votre connexion Internet."
    say "Installation de Python — tapez le mot de passe de votre Mac puis Entrée (il ne s'affiche pas, c'est normal)"
    sudo installer -pkg "$PKG" -target / || fail "L'installation de Python a échoué."
    rm -f "$PKG"
    PY="$(ls /Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13 2>/dev/null)"
    [ -x "$PY" ] || fail "Python a été installé mais reste introuvable. Redémarrez le Mac puis relancez ce script."
  fi
  echo "  Python : $PY ($("$PY" --version 2>&1))"

  # 3. copie dans Applications
  DEST_DIR="/Applications"
  [ -w "$DEST_DIR" ] || DEST_DIR="$HOME/Applications"
  mkdir -p "$DEST_DIR"
  say "Installation de MyLunii dans $DEST_DIR…"
  pkill -f "MyLunii.app/Contents/Resources/app/lunii-qt.py" 2>/dev/null
  if [ "$HERE/MyLunii.app" != "$DEST_DIR/MyLunii.app" ]; then
    rm -rf "$DEST_DIR/MyLunii.app"
    cp -R "$APP_SRC" "$DEST_DIR/" || fail "Copie impossible dans $DEST_DIR."
  fi
  xattr -dr com.apple.quarantine "$DEST_DIR/MyLunii.app" 2>/dev/null

  # 4. préparation + ouverture
  say "Préparation de MyLunii (2 à 5 minutes la première fois)…"
  MYLUNII_PYTHON="$PY" "$DEST_DIR/MyLunii.app/Contents/MacOS/MyLunii" --setup || fail "La préparation a échoué (détails : ~/Library/Application Support/MyLunii/launcher.log)."

  say "C'est prêt ! MyLunii s'ouvre. Vous le retrouverez ensuite dans $DEST_DIR (et le Launchpad)."
  open "$DEST_DIR/MyLunii.app"
}

main "$@"
