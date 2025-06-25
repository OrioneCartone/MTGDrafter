
# AIBot per Draft di Magic: The Gathering

Questo repository contiene il codice per un agente AI basato su architettura **Transformer**, addestrato per partecipare a draft di *Magic: The Gathering*. Il progetto non si limita a creare un modello, ma fornisce un intero **ecosistema** per:

- Generare dati  
- Addestrare il modello  
- Valutare le performance  
- Testare l'agente in un ambiente di draft simulato

L'obiettivo finale è confrontare le performance del nostro **AIBot** contro un avversario di base competente, lo **ScoringBot**, per determinare se un approccio basato su *deep learning* possa superare una solida strategia basata su euristiche.

---

##  Concetti Fondamentali

###  L'Agente AI (AIBot)

- **Architettura**: Basato su un modello **Transformer**, scelto per la sua capacità di pesare l’importanza di diversi input (le carte disponibili e quelle già selezionate).
- **Input del modello**:
  1. Il pacchetto di carte attuale
  2. Il pool di carte già selezionate
  3. Il numero della scelta attuale (es. “scelta 3 del pacchetto 1”)
- **Output**: Un punteggio per ogni carta del pacchetto, rappresentando la preferenza secondo la strategia appresa.

###  L'Avversario di Base (ScoringBot)

Per valutare l’efficacia dell’AIBot, serve un **baseline credibile**. Lo ScoringBot è un bot basato su **euristiche** e **punteggi predefiniti**, e adotta una strategia solida:

- **Valutazione Intrinseca**: Ogni carta ha un punteggio base (es. alto per rimozioni).
- **Contesto del Draft**:
  - *Sinergia di colore*: privilegia le carte in linea con i colori scelti.
  - *Curva di mana*: cerca di mantenere un bilanciamento tra costi delle magie.
  - *Segnali*: interpreta come "segnali" l’arrivo inaspettato di carte forti in pick avanzati.

---

##  Ciclo di Vita del Progetto

Il progetto è suddiviso in 4 fasi principali, eseguibili tramite lo script `fullcycle.sh` oppure manualmente via notebook.

###  Prerequisiti

- Python 3.10+
- Git

###  Fase 1: Download dei Dati
📄 `scripts/download_data.py`

**Cosa fa**:
- Scarica il database completo delle carte da **Scryfall**
- Scarica liste di *cubi* per il draft

**Perché**:
- Le carte servono per avere info dettagliate (costo, tipo, testo, ecc.)
- I cubi offrono ambienti di draft realistici e bilanciati

---

###  Fase 2: Generazione dei Log  
📄 `scripts/generatelogs.py`

**Cosa fa**:
- Simula migliaia di draft con **solo ScoringBot**
- Registra ogni scelta in file di log

**Perché**:
- Crea un dataset di scelte “intelligenti”
- L’AIBot si addestra su queste decisioni, con l’obiettivo di superarle

---

###  Fase 3: Addestramento del Modello  
📄 `scripts/trainmodel.py`

**Cosa fa**:
- Usa i log della Fase 2 per addestrare un **modello Transformer**
- Il modello apprende il contesto delle scelte nel draft

**Perché**:
- Non basta riconoscere carte forti in astratto, serve comprendere il contesto
- Fase intensiva: **l’uso di GPU è fortemente consigliato**

---

###  Fase 4: Valutazione Statistica  
📄 `scripts/evaluatemodel.py`

**Cosa fa**:
- Simula nuovi draft con 1 **AIBot** contro 7 **ScoringBot**
- Analizza i mazzi finali con il **DeckAnalyzer**

**Analisi**:
- Confronta il punteggio medio dei mazzi AIBot vs. ScoringBot
- Esegue un **T-test statistico** per verificare la significatività dei risultati

---

##  Come Eseguire il Progetto

###  Metodo 1: Script Automatico (Locale)

Esegui l’intero ciclo in un colpo con:

```bash
./fullcycle.sh
```

---

###  Metodo 2: Notebook Interattivo (Google Colab)

**Vantaggi**:
- Accesso a **GPU gratuite**
- Possibilità di modificare facilmente gli **iperparametri** (epoche, learning rate, ecc.)

**Il branch `colab-training` contiene**:
- Un notebook di esempio
- Celle per:
  - Clonare il repository
  - Installare le dipendenze
  - Eseguire ogni fase in modo modulare

Ideale per esperimenti e ottimizzazione del modello.
