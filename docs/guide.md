Assolutamente. È il momento perfetto per consolidare tutto ciò che abbiamo costruito con una guida dettagliata. Questo ci darà un quadro chiaro dei progressi e preparerà il terreno per il prossimo grande passo.

Ecco una guida completa che puoi inserire nel tuo `README.md` o in un file separato come `docs/project_summary.md`.

---

## Guida al Progetto MTG Cube Draft AI: Dalla Teoria all'IA Funzionante

Questo documento riassume il percorso di sviluppo del nostro bot per il draft, evidenziando le decisioni strategiche, le sfide superate e lo stato attuale del progetto.

### Fase 1: Costruzione delle Fondamenta (Setup e Simulazione)

L'obiettivo iniziale era creare un ambiente robusto e un "tavolo da gioco" virtuale.

1.  **Infrastruttura del Progetto:**
    *   È stata creata una **struttura di directory professionale** che separa il codice sorgente (`src`), gli script eseguibili (`scripts`), i dati (`data`) e la documentazione (`docs`).
    *   È stato configurato un **ambiente virtuale (`venv`)** e un file `requirements.txt` per garantire un'installazione pulita e riproducibile delle dipendenze (`torch`, `pandas`, etc.).

2.  **Pipeline di Raccolta Dati:**
    *   È stato sviluppato uno script (`scripts/downloaddata.py`) per scaricare automaticamente:
        *   Un **database completo di carte comuni** da Scryfall, che funge da nostra enciclopedia.
        *   Diverse **liste di cubi "Pauper"** da CubeCobra, per fornire varietà di ambienti di draft.
    *   Lo script è stato reso robusto per gestire errori di rete e limiti delle API.

3.  **Ambiente di Simulazione:**
    *   È stata implementata una classe `DraftSimulator` che gestisce un draft completo a 8 giocatori, rispettando le regole di creazione e passaggio delle buste.
    *   È stato creato un `RandomBot` come baseline per i test futuri.

### Fase 2: Sviluppo di un'IA Basata su Regole (Lo "ScoringBot")

Per superare la mancanza di dati di draft umani, abbiamo deciso di creare un "maestro" artificiale da cui imparare.

1.  **Feature Engineering Avanzato (`CardEncoder`):**
    *   Abbiamo costruito un codificatore che trasforma ogni carta in un **vettore numerico ricco di informazioni**.
    *   Questo vettore non include solo dati base (colore, costo, tipo, P/T), ma è stato potenziato per riconoscere:
        *   **21 Keyword cruciali** (es. `Flying`, `Deathtouch`, `Haste`).
        *   **28 Pattern di abilità testuali** (es. `draw a card`, `destroy target creature`, `counter spell`).
    *   Questo ha permesso al nostro sistema di "leggere" le carte in modo molto più dettagliato.

2.  **Creazione dello `ScoringBot` "Maestro":**
    *   Abbiamo sviluppato un bot basato su regole (`ScoringBot`) la cui logica di scelta non è primitiva, ma **olistica**.
    *   Il suo punteggio per una carta è una **somma pesata** di 8 diverse metriche, tra cui sinergia di colore, curva di mana, evasione, rimozioni, vantaggio carte e altre sinergie.
    *   Questo bot agisce come un giocatore esperto ma prevedibile, creando un modello di comportamento di alta qualità da cui imparare.

### Fase 3: Addestramento di un Modello Supervisionato (L'IA attuale)

Con un "maestro" e un codificatore potente, abbiamo addestrato la nostra prima vera rete neurale.

1.  **Generazione di un Dataset Sintetico di Alta Qualità:**
    *   È stato creato lo script `generatelogs.py`, che fa draftare 8 `ScoringBot` l'uno contro l'altro per centinaia di draft.
    *   Ogni singola decisione viene salvata come un file `.json`, contenente lo stato del draft (i vettori ricchi del `pack` e del `pool`) e la carta scelta. Questo è diventato il nostro dataset di training.

2.  **Pipeline di Dati PyTorch (`DataLoader`):**
    *   È stata implementata una classe `DraftLogDataset` per leggere i nostri file di log.
    *   È stata creata una `custom_collate_fn` con **padding** per gestire la natura variabile dei dati di draft (i pack e i pool hanno dimensioni diverse a ogni pick), rendendoli compatibili con PyTorch.

3.  **Architettura della Rete Neurale (`PolicyNetwork`):**
    *   È stato definito un modello basato su MLP (Multi-Layer Perceptron).
    *   L'architettura **riassume il pool di carte** calcolandone la media e poi **concatena** questa informazione con ogni carta della busta, per poi calcolare un punteggio di desiderabilità per ciascuna.

4.  **Training e Risultati:**
    *   È stato creato un ciclo di training completo (`scripts/trainmodel.py`) che ha addestrato il modello sui dati generati. La loss è scesa in modo significativo (es. da 2.3 a 0.7), indicando un apprendimento avvenuto con successo.
    *   Il risultato è un **modello addestrato (`.pth`)**, il "cervello" della nostra IA.

### Fase 4: Valutazione e Stato Attuale

Abbiamo chiuso il cerchio, creando un bot basato sull'IA e un sistema per valutarlo.

1.  **Creazione dell'`AIBot`:**
    *   È stata implementata una classe `AIBot` che carica il modello addestrato e lo usa per prendere decisioni in tempo reale durante un draft.

2.  **Sistema di Valutazione Numerica (`evaluate_deck`):**
    *   È stata sviluppata una funzione sofisticata che analizza un mazzo di 45 carte e gli assegna un **punteggio di qualità** basato su tutte le feature avanzate che abbiamo definito (coerenza, curva, evasione, rimozioni, etc.).

3.  **Risultati Attuali:**
    *   Lanciando `scripts/evaluatemodel.py`, abbiamo messo il nostro `AIBot` contro gli `ScoringBot`.
    *   **Successo:** L'IA ottiene punteggi di mazzo molto alti, dimostrando di aver imparato a dare valore a carte con buone keyword e abilità.
    *   **Limite Identificato:** L'IA, pur riconoscendo le carte forti, mostra una **disciplina di colore inferiore** rispetto allo `ScoringBot`. Tende a prendere la "carta migliore" in assoluto, faticando a consolidare un piano di colori ristretto.

### Prossimi Passi

Abbiamo raggiunto il limite del nostro modello attuale. Per superare la "mancanza di disciplina" e insegnare all'IA a comprendere le sinergie più profonde, il prossimo passo è evolvere l'architettura della rete neurale, passando a un **modello basato su Transformer**.