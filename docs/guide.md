Questo repository contiene il codice per un agente AI basato su architettura Transformer, addestrato per partecipare a draft di Magic: The Gathering. Il progetto non si limita a creare un modello, ma fornisce un intero ecosistema per generare dati, addestrare, valutare e testare l'agente in un ambiente di draft simulato.

L'obiettivo finale è confrontare le performance del nostro AIBot contro un avversario di base competente, lo ScoringBot, per determinare se l'approccio basato su deep learning può superare una solida strategia basata su euristiche.

Concetti Fondamentali
Prima di eseguire il progetto, è utile comprendere i due attori principali e l'ambiente in cui operano.

1. L'Agente AI (AIBot)
Architettura: Il cuore dell'agente è un modello Transformer. Questa architettura è stata scelta per la sua capacità di pesare l'importanza di input diversi (le carte nel pacchetto e nel mazzo) per prendere una decisione contestuale.
Input: Per ogni scelta, il modello riceve tre informazioni:
Il pacchetto di carte attuale.
Il pool di carte già selezionate dal giocatore.
Il numero della scelta attuale (es. "scelta 3 del pacchetto 1").
Output: Il modello produce un punteggio per ogni carta nel pacchetto, indicando la scelta migliore secondo la sua strategia appresa.
2. L'Avversario di Base (ScoringBot)
Per valutare se il nostro AIBot è efficace, non basta confrontarlo con un bot che sceglie a caso. Serve un avversario di base (baseline) credibile. Lo ScoringBot è un bot basato su euristiche e punteggi predefiniti:

Valutazione Intrinseca: Assegna un punteggio base a ogni carta in base alle sue abilità (es. una carta che distrugge creature ha un punteggio "removal" alto).
Contesto del Draft: Applica bonus e malus contestuali:
Sinergia di Colore: Privilegia le carte che si allineano ai colori principali del mazzo in costruzione.
Curva di Mana: Cerca di bilanciare il costo delle magie per avere un mazzo giocabile.
Segnali: Riconosce se una carta potente arriva inaspettatamente a un punto avanzato del draft, interpretandolo come un "segnale" che quel colore è poco conteso.
Questo bot rappresenta una strategia solida e consapevole, rendendo la valutazione finale molto più significativa.

Il Ciclo di Vita del Progetto
Il progetto è strutturato in un ciclo di 4 fasi principali, automatizzabili tramite lo script fullcycle.sh o eseguibili passo-passo in un notebook.

Prerequisiti
Assicurati di avere Python 3.10+ e Git installati.

Clona il Repository

Prepara l'Ambiente Virtuale

Fase 1: Download dei Dati (scripts/download_data.py)
Il primo passo è ottenere i dati grezzi necessari.

Cosa fa: Scarica un database completo di carte di Magic (da Scryfall) e diverse liste di "cubi" (set di carte personalizzati per il draft).
Perché: Il database serve per avere tutte le informazioni di ogni carta (costo, tipo, testo, etc.). I cubi servono come ambienti di draft vari e bilanciati per le simulazioni.
Fase 2: Generazione dei Log (scripts/generatelogs.py)
L'AI ha bisogno di dati su cui addestrarsi. Non potendo usare log di draft umani, li generiamo.

Cosa fa: Esegue migliaia di draft simulati usando solo ScoringBot. Ogni scelta fatta da ogni bot viene salvata in un file di log.
Perché: Questo crea un vasto dataset di scelte "intelligenti" (secondo la logica dello ScoringBot). L'obiettivo del nostro AIBot sarà imparare a replicare e, si spera, migliorare queste decisioni.
Fase 3: Addestramento del Modello (scripts/trainmodel.py)
Questa è la fase di deep learning vera e propria.

Cosa fa: Carica i log generati nella fase precedente e li usa per addestrare il modello Transformer. Il modello impara a prevedere quale carta uno ScoringBot avrebbe scelto in una data situazione.
Perché: Allenandosi su esempi di scelte contestuali, il modello non impara solo a riconoscere le carte "forti" in astratto, ma a capire quale carta è la migliore per il mazzo che sta costruendo in quel preciso momento. Questa fase è computazionalmente intensiva e beneficia enormemente di una GPU.
Fase 4: Valutazione Statistica (scripts/evaluatemodel.py)
È il momento del giudizio. Il modello addestrato è davvero migliore della sua controparte basata su euristiche?

Cosa fa: Esegue un nuovo set di simulazioni di draft. In ogni draft, un giocatore è il nostro AIBot e gli altri 7 sono ScoringBot.
Analisi: Al termine di ogni draft, i mazzi finali vengono analizzati da un DeckAnalyzer che assegna un punteggio di qualità basato su sinergie, curva di mana e potenza delle carte.
Risultato: Lo script confronta il punteggio medio dei mazzi dell'AIBot con quello medio dei mazzi degli ScoringBot. Esegue anche un T-test statistico per determinare se la differenza di performance è statisticamente significativa o solo frutto del caso.
Come Eseguire il Progetto
Metodo 1: Script Automatico (Locale)
Per eseguire l'intero ciclo in un colpo solo, usa lo script fullcycle.sh.

Metodo 2: Notebook Interattivo (Google Colab)
Per sperimentare, specialmente con l'addestramento, l'uso di Google Colab è fortemente consigliato per l'accesso a GPU gratuite. Il repository contiene un branch colab-training e un notebook di esempio che permette di:

Clonare il repository.
Installare le dipendenze.
Eseguire le fasi di preparazione, addestramento e valutazione in celle separate.
Modificare al volo gli iperparametri (es. numero di epoche, learning rate) per iterare rapidamente sugli esperimenti senza modificare i file di progetto.
Questo approccio è ideale per la ricerca e l'ottimizzazione del modello.