#!/bin/bash

# ===================================================================
#      Script per l'Esecuzione del Ciclo di Training
#
# Uso:
#   ./run_full_cycle.sh            - Esegue l'intero ciclo da zero (cleanup -> generate -> train -> evaluate)
#   ./run_full_cycle.sh generate   - Esegue da 'generate' in poi (cleanup -> generate -> train -> evaluate)
#   ./run_full_cycle.sh train      - Esegue da 'train' in poi (train -> evaluate)
#   ./run_full_cycle.sh evaluate   - Esegue solo la fase di 'evaluate'
# ===================================================================

set -e

# --- Definizione delle Funzioni per ogni Fase ---
# Suddividere in funzioni rende lo script più leggibile e modulare

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

# --- Logica Principale ---

# Controlla il primo argomento passato allo script ($1)
START_PHASE=${1:-all} # Se non viene passato nessun argomento, il default è 'all'

# Attiva sempre l'ambiente
setup_env
echo

# Esegue le fasi in base al punto di partenza scelto
if [[ "$START_PHASE" == "all" || "$START_PHASE" == "cleanup" || "$START_PHASE" == "generate" ]]; then
    do_cleanup
    echo
    do_generate_logs
    echo
    # Dopo aver generato i log, dobbiamo per forza fare il training e la valutazione
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
    echo "Uso: ./run_full_cycle.sh [generate|train|evaluate]"
    exit 1
fi

echo
echo "🎉 Ciclo eseguito con successo!"
