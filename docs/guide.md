Guida al Progetto: Dalle Idee ai Dati di Training

Questa guida documenta il viaggio fatto finora per costruire le fondamenta del nostro MTG Cube Draft AI. Abbiamo trasformato un'idea astratta in un dataset concreto, pronto per l'addestramento di un modello di machine learning.
Fase 1: Costruzione dell'Ambiente e Raccolta Dati

L'obiettivo iniziale era creare un "universo" in cui il nostro futuro bot potesse esistere e interagire.

    Setup dell'Infrastruttura:
        È stata definita una struttura di cartelle chiara e scalabile, separando codice (src), dati (data), script (scripts) e configurazioni (config).
        È stato creato un ambiente virtuale (venv) per isolare le dipendenze del progetto, garantendo la riproducibilità.
        È stato redatto un file requirements.txt per gestire tutte le librerie necessarie (torch, pandas, etc.).

    Raccolta dei Dati Grezzi:
        Abbiamo scritto uno script (scripts/download_data.py) che recupera due tipi di dati fondamentali:
            Il Dizionario delle Carte: Un file JSON completo da Scryfall con tutte le informazioni su ogni carta di Magic.
            Le Liste dei Cubi: Liste di carte specifiche per i cubi che vogliamo draftare, scaricate da CubeCobra.
        Abbiamo reso gli script di download robusti, gestendo errori di rete e limiti delle API.

Fase 2: Creazione del Simulatore di Draft

Con i dati a disposizione, abbiamo costruito il "tavolo da gioco".

    Simulatore di Regole:
        È stata creata la classe DraftSimulator (src/environment/draft_simulator.py), un "arbitro" che gestisce l'intero processo di un draft (creazione buste, passaggi, turni) senza conoscere le regole del gioco di Magic.

    Agenti di Baseline:
        RandomBot: Un bot che sceglie carte a caso. Utile come baseline per misurare le performance future.
        ScoringBot: Il nostro primo bot "intelligente", basato su regole semplici (euristiche). Questo bot è stato fondamentale perché:
            Ci ha permesso di creare un agente con un comportamento sensato (es. rimanere nei propri colori).
            È diventato lo strumento per generare i nostri dati di training.

    Feature Engineering:
        È stato creato un CardEncoder (src/features/card_encoders.py) per tradurre le informazioni testuali di una carta (colore, costo, tipo, P/T) in un vettore numerico, il linguaggio che i modelli di machine learning capiscono.

Fase 3: Generazione del Dataset di Training Sintetico

Questo è stato il passo cruciale che ci ha permesso di superare la mancanza di dati reali per il nostro cubo.

    Il Problema: Non avevamo log di draft umani specifici per il Pauper Cube.

    La Soluzione (Bootstrap): Abbiamo usato il nostro ScoringBot per creare dati da solo.
        È stato creato lo script scripts/generate_logs.py.
        Questo script fa draftare 8 ScoringBot l'uno contro l'altro per un numero N di volte.
        Ogni singola scelta di ogni bot viene registrata da un DraftLogger.

    Il Risultato: Una cartella (data/processed/draft_logs/) piena di migliaia di file JSON. Ogni file rappresenta un singolo punto dati per il nostro training, contenente:
        Lo stato del draft al momento della scelta (i vettori del pack e del pool).
        L'azione scelta (il vettore della carta presa).

Fase 4: Preparazione dei Dati per il Training

Abbiamo trasformato il nostro tesoro di file JSON in un formato pronto per PyTorch.

    Gestione dei Dati Variabili: Abbiamo capito che ogni campione di dati ha dimensioni diverse (il pack e il pool cambiano dimensione a ogni pick).
    DataLoader Personalizzato:
        È stata creata la classe DraftLogDataset in src/data/loaders.py per leggere i singoli file di log.
        È stata implementata una custom_collate_fn che risolve il problema delle dimensioni variabili tramite padding, assicurando che ogni batch di dati abbia una forma consistente.

Dove Siamo Ora

Abbiamo completato con successo tutta la pipeline di preparazione dei dati. Abbiamo un DataLoader funzionante che può servire batch di dati di training, puliti e pronti, alla nostra futura rete neurale.

Abbiamo costruito il "tagliere" e preparato tutti gli ingredienti. Ora siamo pronti per iniziare a cucinare: definire il modello e avviare il training.