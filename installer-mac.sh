#!/bin/bash
# Installe MyLunii sur Mac et crée un raccourci sur le Bureau.
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
  DEST="$HOME/MyLunii"
  OLD_DEST="$HOME/Lunii.QT"
  SHORTCUT="$HOME/Desktop/MyLunii.command"
  OLD_SHORTCUT="$HOME/Desktop/Lunii.QT.command"
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
  say "Téléchargement de MyLunii…"
  TMP="$(mktemp -d)"
  curl -fsSL "$ZIP_URL" -o "$TMP/lunii.zip" || fail "Téléchargement impossible. Vérifiez votre connexion Internet."
  unzip -q "$TMP/lunii.zip" -d "$TMP" || fail "Archive illisible."
  SRC="$(find "$TMP" -maxdepth 1 -type d -name 'Lunii.QT-*' | head -n 1)"
  [ -d "$SRC" ] || fail "Archive inattendue."

  # ancienne installation (nom « Lunii.QT ») : on la déplace sous le nouveau nom
  if [ ! -d "$DEST" ] && [ -d "$OLD_DEST" ] && [ -f "$OLD_DEST/lunii-qt.py" ]; then
    mv "$OLD_DEST" "$DEST"
    rm -rf "$DEST/.venv"     # l'environnement Python dépend de son dossier : on le refait
  fi
  if [ -d "$DEST" ]; then
    # mise à jour : on garde l'environnement Python déjà prêt
    [ -d "$DEST/.venv" ] && mv "$DEST/.venv" "$TMP/.venv-keep"
    mv "$DEST" "$TMP/old-install"
  fi
  mv "$SRC" "$DEST" || fail "Impossible de copier l'application dans $DEST"
  [ -d "$TMP/.venv-keep" ] && mv "$TMP/.venv-keep" "$DEST/.venv"
  chmod +x "$DEST/MyLunii.app/Contents/MacOS/MyLunii" 2>/dev/null
  xattr -cr "$DEST" 2>/dev/null
  echo "  Installé dans $DEST"

  # 3. Environnement Python (quelques minutes la première fois)
  cd "$DEST" || fail "Dossier introuvable."
  if [ ! -x ".venv/bin/python" ]; then
    say "Préparation de Python pour MyLunii (2 à 5 minutes la première fois)…"
    "$PY" -m venv .venv || fail "Impossible de créer l'environnement Python."
  fi
  .venv/bin/python -m pip install --upgrade pip -q
  .venv/bin/python -m pip install -r requirements-launcher.txt -q || fail "L'installation des bibliothèques a échoué. Vérifiez votre connexion Internet et relancez la commande."

  say "Traductions françaises et ressources…"
  .venv/bin/pyside6-lrelease locales/fr_FR.ts -qm locales/fr_FR.qm >/dev/null 2>&1 || echo "  (traductions non compilées : l'interface sera en anglais)"
  .venv/bin/pyside6-rcc resources.qrc -o resources_rc.py || fail "Impossible de préparer les ressources."
  touch ".venv/.mylunii-ready-$(shasum requirements-launcher.txt | cut -c1-12)"

  # 4. Raccourci sur le Bureau
  say "Création du raccourci sur le Bureau…"
  cat > "$SHORTCUT" <<EOF
#!/bin/bash
# Raccourci MyLunii : double-cliquez pour ouvrir l'application.
# Laissez cette fenêtre ouverte (vous pouvez la réduire) tant que vous utilisez MyLunii.
cd "$DEST" || exit 1
echo "Ouverture de MyLunii…"
exec .venv/bin/python lunii-qt.py
EOF
  chmod +x "$SHORTCUT"
  # l'ancien raccourci pointait vers l'ancien dossier : on le range pour ne pas l'avoir en double
  if [ -f "$OLD_SHORTCUT" ] && [ "$OLD_SHORTCUT" != "$SHORTCUT" ]; then
    mkdir -p "$DEST/_anciens-raccourcis" && mv "$OLD_SHORTCUT" "$DEST/_anciens-raccourcis/" 2>/dev/null
  fi

  rm -rf "$TMP"
  say "C'est prêt !"
  echo "  Double-cliquez sur « MyLunii » sur votre Bureau pour ouvrir l'application."
  echo "  Pour mettre à jour plus tard, relancez simplement la même commande."
  echo
  open "$SHORTCUT"
}

main "$@"
