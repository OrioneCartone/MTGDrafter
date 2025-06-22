#!/bin/bash

# ===================================================================
#     Script per Creare un Archivio .zip Pulito del Codice Sorgente
# ===================================================================

set -e

PROJECT_DIR_NAME=$(basename "$PWD")
OUTPUT_ZIP_FILE="${PROJECT_DIR_NAME}-source-$(date +%Y%m%d).zip"

echo "▶️  Creazione dell'archivio '${OUTPUT_ZIP_FILE}'..."
echo "${PROJECT_DIR_NAME}"
echo "    Includendo tutto il contenuto della cartella corrente..."

# La sintassi -x 'cartella/*' è più robusta
# Escludiamo tutte le cartelle che non sono codice sorgente.
zip -r "zippone.zip" . \
    -x 'venv/*' \
    -x 'data/*' \
    -x 'models/*' \
    -x 'logs/*' \
    -x '.git/*' \
    -x '__pycache__/*' \
    -x '*/__pycache__/*' \
    -x '*/*/__pycache__/*' \
    -x '.ipynb_checkpoints/*' \
    -x 'notebooks/.ipynb_checkpoints/*' \
    -x '*.zip' # Esclude se stesso se già presente

echo
echo "✅ Archivio creato con successo in: ../${OUTPUT_ZIP_FILE}"
echo "🎉 Fatto!"
