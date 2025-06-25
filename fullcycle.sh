#!/bin/bash

# ===================================================================
#      Script per l'Esecuzione del Ciclo di Training
#
# Uso:
#   ./fullcycle.sh          - Esegue il ciclo completo (default)
#   ./fullcycle.sh generate - Parte dalla generazione dei log
#   ./fullcycle.sh train    - Parte dall'addestramento
#   ./fullcycle.sh evaluate - Esegue solo la valutazione
#   ./fullcycle.sh cleanup  - Esegue solo la pulizia
# ===================================================================

set -e # Interrompe lo script se un comando fallisce

# --- Funzioni Helper ---

setup_env() {
    # MODIFICA: Rileva automaticamente l'ambiente Google Colab.
    # Se la variabile d'ambiente COLAB_GPU esiste, siamo su Colab e saltiamo la gestione di venv.
    if [ -n "$COLAB_GPU" ]; then
        echo "✅ Rilevato ambiente Google Colab. Salto l'attivazione di 'venv'."
        return
    fi

    # Codice originale per l'ambiente locale
    echo "▶️  FASE 0: Attivazione dell'ambiente virtuale..."
    if [ ! -f "venv/bin/activate" ]; then
        echo "❌ Errore: La cartella 'venv' non è stata trovata."
        echo "Esegui 'python3 -m venv venv' e 'pip install -r requirements.txt'"
        exit 1
    fi
    source venv/bin/activate
    echo "✅ Ambiente 'venv' attivato."
}

do_cleanup() {
    echo "▶️  FASE 1: Pulizia delle cartelle di output..."
    rm -rf data/processed/pauper_generalist_logs/*
    rm -rf models/pauper_generalist/*
    # Crea un file .gitkeep per assicurarsi che le cartelle non vengano eliminate da Git
    touch data/processed/pauper_generalist_logs/.gitkeep
    touch models/pauper_generalist/.gitkeep
    echo "✅ Cartelle di output pulite."
}

do_download() {
    echo "▶️  FASE 2: Download dei dati grezzi..."
    python scripts/download_data.py
    echo "✅ Dati grezzi scaricati."
}

do_generate_logs() {
    echo "▶️  FASE 2.5: Generazione dei log di draft per il training..."
    python scripts/generatelogs.py
    echo "✅ Log di training generati."
}

do_train_model() {
    echo "▶️  FASE 3: Addestramento del nuovo modello..."
    python scripts/trainmodel.py
    echo "✅ Modello addestrato e salvato."
}

do_evaluate_model() {
    echo "▶️  FASE 4: Valutazione del modello addestrato..."
    python scripts/evaluatemodel.py
    echo "✅ Valutazione completata."
}


# --- Logica Principale ---

# Attiva l'ambiente (la funzione ora gestisce Colab)
setup_env

START_PHASE=${1:-all} # Default a 'all' se non viene fornito nessun argomento

echo "--- Avvio Ciclo di Esecuzione (Fase iniziale: $START_PHASE) ---"

if [[ "$START_PHASE" == "all" ]]; then
    do_cleanup
    echo
    do_download
    echo
    do_generate_logs
    echo
    do_train_model
    echo
    do_evaluate_model
elif [[ "$START_PHASE" == "cleanup" ]]; then
    do_cleanup
elif [[ "$START_PHASE" == "generate" ]]; then
    do_generate_logs
    echo
    do_train_model
    echo
    do_evaluate_model
elif [[ "$START_PHASE" == "train" ]]; then
    do_train_model
    echo
    do_evaluate_model
elif [[ "$START_PHASE" == "evaluate" ]]; then
    do_evaluate_model
else
    echo "❌ Argomento non valido: '$START_PHASE'"
    echo "Uso: ./fullcycle.sh [generate|train|evaluate|cleanup]"
    exit 1
fi

echo
echo "🎉 Ciclo eseguito con successo!"