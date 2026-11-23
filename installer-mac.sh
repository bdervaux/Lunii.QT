#!/bin/bash
# Installe Lunii.QT (nouvelle interface) sur Mac et crée un raccourci sur le Bureau.
#
# Dans le Terminal :
#   curl -fsSL https://raw.githubusercontent.com/bdervaux/Lunii.QT/nouvelle-interface/installer-mac.sh | bash
#
# Rien n'est téléchargé par le navigateur : macOS ne bloque donc pas l'application.

set -u

# everything is inside main() so that "curl … | bash" reads the whole script before running it
main() {
  BRANCH="nouvelle-interface"
  ZIP_URL="https://github.com/bdervaux/Lunii.QT/archive/refs/heads/${BRANCH}.zip"
  DEST="$HOME/Lunii.QT"
  SHORTCUT="$HOME/Desktop/Lunii.QT.command"
  export PATH="/Library/Frameworks/Python.framework/Versions/Current/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"

  say()  { printf "\n\033[1;35m▶ %s\033[0m\n" "$1"; }
  fail() { printf "\n\033[1;31m✖ %s\033[0m\n\n" "$1"; exit 1; }

  # 1. Python
  say "Recherche de Python…"
  PY=""
  for candidate in python3.12 python3.11 python3.10 python3.13 python3; do
    path="$(command -v "$candidate" 2>/dev/null)" || continue
    [ -z "$path" ] && continue
    # /usr/bin/python3 n'est qu'un raccourci quand les outils Apple ne sont pas installés
    if [ "$path" = "/usr/bin/python3" ] && ! xcode-select -p >/dev/null 2>&1; then
      continue
    fi
    if "$path" -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" >/dev/null 2>&1; then
      PY="$path"; break
    fi
  done
  if [ -z "$PY" ]; then
    open "https://www.python.org/downloads/macos/"
    fail "Python n'est pas installé. La page de téléchargement vient de s'ouvrir : installez Python 3.12, puis relancez la même commande."
  fi
  echo "  Python trouvé : $PY ($("$PY" --version 2>&1))"

  # 2. Code de l'application
  say "Téléchargement de Lunii.QT…"
  TMP="$(mktemp -d)"
  curl -fsSL "$ZIP_URL" -o "$TMP/lunii.zip" || fail "Téléchargement impossible. Vérifiez votre connexion Internet."
  unzip -q "$TMP/lunii.zip" -d "$TMP" || fail "Archive illisible."
  SRC="$(find "$TMP" -maxdepth 1 -type d -name 'Lunii.QT-*' | head -n 1)"
  [ -d "$SRC" ] || fail "Archive inattendue."

  if [ -d "$DEST" ]; then
    # mise à jour : on garde l'environnement Python déjà prêt
    [ -d "$DEST/.venv" ] && mv "$DEST/.venv" "$TMP/.venv-keep"
    mv "$DEST" "$TMP/old-install"
  fi
  mv "$SRC" "$DEST" || fail "Impossible de copier l'application dans $DEST"
  [ -d "$TMP/.venv-keep" ] && mv "$TMP/.venv-keep" "$DEST/.venv"
  chmod +x "$DEST/Lunii.QT.app/Contents/MacOS/Lunii.QT" 2>/dev/null
  xattr -cr "$DEST" 2>/dev/null
  echo "  Installé dans $DEST"

  # 3. Environnement Python (quelques minutes la première fois)
  cd "$DEST" || fail "Dossier introuvable."
  if [ ! -x ".venv/bin/python" ]; then
    say "Préparation de Python pour Lunii.QT (2 à 5 minutes la première fois)…"
    "$PY" -m venv .venv || fail "Impossible de créer l'environnement Python."
  fi
  .venv/bin/python -m pip install --upgrade pip -q
  .venv/bin/python -m pip install -r requirements-launcher.txt -q || fail "L'installation des bibliothèques a échoué. Vérifiez votre connexion Internet et relancez la commande."

  say "Traductions françaises et ressources…"
  .venv/bin/pyside6-lrelease locales/fr_FR.ts -qm locales/fr_FR.qm >/dev/null 2>&1 || echo "  (traductions non compilées : l'interface sera en anglais)"
  .venv/bin/pyside6-rcc resources.qrc -o resources_rc.py || fail "Impossible de préparer les ressources."
  touch .venv/.lunii-ready

  # 4. Raccourci sur le Bureau
  say "Création du raccourci sur le Bureau…"
  cat > "$SHORTCUT" <<EOF
#!/bin/bash
# Raccourci Lunii.QT : double-cliquez pour ouvrir l'application.
# Laissez cette fenêtre ouverte (vous pouvez la réduire) tant que vous utilisez Lunii.QT.
cd "$DEST" || exit 1
echo "Ouverture de Lunii.QT…"
exec .venv/bin/python lunii-qt.py
EOF
  chmod +x "$SHORTCUT"

  rm -rf "$TMP"
  say "C'est prêt !"
  echo "  Double-cliquez sur « Lunii.QT » sur votre Bureau pour ouvrir l'application."
  echo "  Pour mettre à jour plus tard, relancez simplement la même commande."
  echo
  open "$SHORTCUT"
}

main "$@"
