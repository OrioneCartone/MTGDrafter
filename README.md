# MTG Cube Draft AI

Questo progetto mira a sviluppare un'intelligenza artificiale in grado di draftare un cubo di Magic: The Gathering. Il sistema è progettato per essere modulare, partendo dalla raccolta dati e simulazione, fino all'addestramento di modelli di machine learning complessi.

## Roadmap e Stato Attuale

-   [x] **Fase 1.1: Data Collection**: Creati script per scaricare dati essenziali da fonti esterne.
    -   [x] Download di un database di carte completo da **Scryfall API**.
    -   [x] Download di liste di cubi specifici da **CubeCobra API**.
    -   [x] Implementati meccanismi di robustezza (retry, user-agent) per gestire le API.
-   [x] **Fase 1.2: Simulation Environment**: Costruito un simulatore di draft completo.
    -   [x] Definite le strutture dati per `Card`, `Player`, e `DraftPack`.
    -   [x] Creato un `RandomBot` come agente di baseline che sceglie carte a caso.
    -   [x] Implementato un `DraftSimulator` che gestisce l'intero processo di un draft (creazione buste, passaggi a destra/sinistra, turni).
-   [x] **Fase 2.1: Feature Engineering**: Iniziata la traduzione delle carte in un formato numerico.
    -   [x] Creato un `CardEncoder` per estrarre features come identità di colore, CMC, tipo di carta e P/T.
-   [ ] **Fase 2.2: Model Definition**: Prossimo passo: definire l'architettura del modello AI.
-   [ ] **Fase 3: Training & Evaluation**: Addestrare e valutare il bot AI.

---

## Setup dell'Ambiente di Sviluppo

Per eseguire questo progetto, è necessario configurare un ambiente Python isolato.

### Prerequisiti

-   Python 3.10+
-   `venv` (incluso in Python)
-   Strumenti di compilazione per pacchetti C:
    ```bash
    sudo apt-get update && sudo apt-get install python3-dev build-essential
    ```

### Installazione

1.  **Clona il repository:**
    ```bash
    git clone <URL_DEL_TUO_REPO>
    cd mtg-cube-ai
    ```

2.  **Crea un ambiente virtuale:**
    Questo crea una cartella `venv` che conterrà tutte le dipendenze del progetto, mantenendo pulito il tuo sistema.
    ```bash
    python3 -m venv venv
    ```

3.  **Attiva l'ambiente virtuale:**
    Devi eseguire questo comando ogni volta che apri un nuovo terminale per lavorare al progetto.
    ```bash
    source venv/bin/activate
    ```
    La tua riga di comando dovrebbe ora mostrare un prefisso `(venv)`.

4.  **Installa le dipendenze:**
    Questo comando legge il file `requirements.txt` e installa tutte le librerie necessarie all'interno del tuo ambiente virtuale.
    ```bash
    pip install -r requirements.txt
    ```

---

## Utilizzo

### 1. Scaricare i Dati

Prima di tutto, esegui lo script per scaricare il database delle carte e le liste dei cubi. I file verranno salvati nella cartella `data/`.
```bash
python scripts/download_data.py

python scripts/simulate_draft.py
# Eseguire da terminale (nella cartella del progetto, con venv attivo)
jupyter lab
