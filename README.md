# MTG Cube Draft AI

Questo progetto ha l'obiettivo di creare un'intelligenza artificiale in grado di draftare un cubo di Magic: The Gathering. Il sistema è progettato per essere costruito passo dopo passo, partendo dalle fondamenta (raccolta dati e simulazione) fino all'addestramento di modelli di machine learning.

## Stato del Progetto

Abbiamo completato le prime, fondamentali fasi del progetto.

*   ✅ **Raccolta Dati**: Script robusti per scaricare dati da Scryfall (database carte) e CubeCobra (liste cubi).
*   ✅ **Simulatore di Draft**: Un ambiente di simulazione completo che gestisce un draft a 8 giocatori, con creazione di buste e passaggi corretti.
*   ✅ **Bot di Baseline**:
    *   `RandomBot`: Un agente che sceglie carte a caso, utile per i test.
    *   `ScoringBot`: Un bot basato su regole semplici (coerenza di colori, costo di mana) che drafta in modo sorprendentemente coerente.
*   ✅ **Feature Engineering**: Un `CardEncoder` che trasforma le informazioni di una carta in un vettore numerico, pronto per essere usato da un modello.
*   ✅ **Generazione Dati Sintetici**: Uno script (`generate_logs.py`) che usa il simulatore per far draftare 8 `ScoringBot` l'uno contro l'altro, generando migliaia di log di draft. **Questi log formeranno il nostro dataset di addestramento.**

In pratica, non solo abbiamo un "tavolo da gioco" virtuale, ma abbiamo anche un metodo per creare un dataset di addestramento su misura per il nostro cubo, risolvendo il problema della mancanza di dati reali.

## Come Usare il Progetto

Per replicare il progetto, segui questi passaggi.

### 1. Preparazione dell'Ambiente

Assicurati di avere Python 3.10+ e gli strumenti di compilazione necessari. Su un sistema basato su Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install python3-dev build-essential

# 1. Crea un ambiente virtuale per isolare le dipendenze
python3 -m venv venv

# 2. Attiva l'ambiente (da fare ogni volta che apri un nuovo terminale)
source venv/bin/activate

# 3. Installa tutte le librerie necessarie
pip install -r requirements.txt

python scripts/download_data.py

python scripts/generate_logs.py
## (Optional) python scripts/simulate_draft.py
