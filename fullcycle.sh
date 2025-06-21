#!/bin/bash

# ===================================================================
#      Script per l'Esecuzione del Ciclo di Training
#
# Uso:
#   ./fullcycle.sh            - Esegue l'intero ciclo da zero
#   ./fullcycle.sh generate   - Salta la pulizia e il download, rigenera i dati
#   ./fullcycle.sh train      - Salta tutto e parte dal training
#   ./fullcycle.sh evaluate   - Esegue solo la fase di valutazione
# ===================================================================

set -e

# --- Definizione delle Funzioni per ogni Fase ---

setup_env() {
    echo "▶️  FASE 0: Attivazione dell'ambiente virtuale..."
    if [ ! -d "venv" ]; then
        echo "❌ Errore: La cartella 'venv' non è stata trovata."
        echo "Esegui 'python3 -m venv venv' e 'pip install -r requirements.txt' prima."
        exit 1
    fi
    source venv/bin/activate
    echo "✅ Ambiente 'venv' attivato."
}

do_cleanup() {
    echo "▶️  FASE 1: Pulizia degli artefatti precedenti..."
    python scripts/cleanup.py
    echo "✅ Pulizia completata."
}

# --- FUNZIONE MANCANTE AGGIUNTA QUI ---
do_download() {
    echo "▶️  FASE 1.5: Download dei dati grezzi (se necessario)..."
    python scripts/downloaddata.py
    echo "✅ Download dati completato."
}
# --- FINE AGGIUNTA ---

do_generate_logs() {
    echo "▶️  FASE 2: Generazione del dataset di training..."
    python scripts/generatelogs.py
    echo "✅ Dataset generato con successo."
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

# --- Logica Principale Aggiornata ---
START_PHASE=${1:-all}

setup_env
echo

if [[ "$START_PHASE" == "all" || "$START_PHASE" == "cleanup" ]]; then
    # Il ciclo completo parte dalla pulizia e include il download
    do_cleanup
    echo
    do_download
    echo
    do_generate_logs
    echo
    do_train_model
    echo
    do_evaluate_model
elif [[ "$START_PHASE" == "generate" ]]; then
    # Se voglio solo rigenerare i log, non serve pulire o riscaricare tutto
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
