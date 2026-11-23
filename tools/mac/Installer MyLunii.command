#!/bin/bash
# Double-cliquez sur ce fichier pour installer et ouvrir MyLunii.
cd "$(dirname "$0")" || exit 1
bash ./installer-mylunii.sh
status=$?
echo
read -n 1 -s -r -p "Appuyez sur une touche pour fermer cette fenêtre…"
echo
exit $status
