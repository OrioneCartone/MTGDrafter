from pathlib import Path
import sys
import json
import torch
import random
import time
from tqdm import tqdm
import pandas as pd # Useremo pandas per una bella visualizzazione finale

# Aggiunge la root del progetto al path di Python
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

# Importa tutti i moduli necessari
from src.environment.draftsimulator import DraftSimulator
from src.environment.opponents import ScoringBot, AIBot
from src.environment.draft import Player
from src.utils.constants import FEATURE_SIZE
from src.evaluation.evaluator import evaluate_deck

# --- Configurazione della Valutazione ---
DATA_DIR = PROJECT_ROOT / "data"
MODEL_PATH = PROJECT_ROOT / "models" / "experiments" / "transformer_v1" / "model_final.pth"
CARD_DB_PATH = DATA_DIR / "external" / "scryfall_commons.json"
CUBE_LIST_PATH = DATA_DIR / "raw" / "cube_lists" / "thepaupercube.json"

NUM_PLAYERS = 8
NUM_SIMULATIONS = 100 # Numero di draft da simulare per avere dati statistici

def load_json_file(path: Path):
    """Carica un file JSON e gestisce l'errore se non esiste."""
    if not path.exists():
        print(f"ERRORE: Il file {path} non è stato trovato.")
        sys.exit(1)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


class EvaluationSuite:
    """Gestisce l'esecuzione di N simulazioni e l'aggregazione dei risultati."""
    def __init__(self, cube_full_details, model_path):
        self.cube_full_details = cube_full_details
        self.model_path = model_path
        self.results = []

    def run_single_simulation(self, draft_id: int):
        """Esegue un singolo draft completo."""
        # Creiamo un seed diverso per ogni simulazione per garantire la varietà
        seed = int(time.time() * 1000) + draft_id
        random.seed(seed)
        
        # Configurazione del tavolo: 1 AI vs 7 ScoringBot
        bots = []
        ai_player = Player(player_id=0)
        ai_bot = AIBot(player=ai_player, model_path=self.model_path)
        bots.append(ai_bot)
        for i in range(1, NUM_PLAYERS):
            bots.append(ScoringBot(Player(player_id=i)))
            
        simulator = DraftSimulator(
            cube_list=list(self.cube_full_details), # Passa una copia del cubo
            bots=bots,
            draft_id=draft_id
        )
        final_pools = simulator.run_draft(verbose=False) # Eseguiamo in modalità silenziosa

        # Analizza e salva i risultati di questo draft
        for player_id, player in final_pools.items():
            bot_type = "AI" if player_id == 0 else "Scoring"
            deck_metrics = evaluate_deck(player.pool)

            # Forza la presenza di tutte le metriche richieste
            DEFAULT_KEYS = [
                "final_score", "color_consistency", "avg_cmc", "creature_count",
                "evasion_score", "removal_score", "card_advantage_score"
            ]

            if not isinstance(deck_metrics, dict):
                print(f"[AVVISO] evaluate_deck ha restituito un valore non valido per il player {player_id}.")
                deck_metrics = {}

            for key in DEFAULT_KEYS:
                deck_metrics.setdefault(key, 0.0)
            
            self.results.append({
                "draft_id": draft_id,
                "bot_type": bot_type,
                **deck_metrics # Aggiunge tutte le metriche al dizionario
            })

    def run_all(self, num_sims: int):
        """Esegue tutte le simulazioni e stampa l'analisi finale."""
        print(f"\n--- Avvio suite di valutazione per {num_sims} simulazioni ---")
        
        for i in tqdm(range(num_sims), desc="Simulando Drafts"):
            self.run_single_simulation(i)
            
        self.analyze_results()

    def analyze_results(self):
        """Converte i risultati in un DataFrame pandas e stampa le statistiche aggregate."""
        if not self.results:
            print("Nessun risultato da analizzare.")
            return

        df = pd.DataFrame(self.results)
        
        # Raggruppa i risultati per tipo di bot e calcola le medie
        summary = df.groupby('bot_type').agg({
            'final_score': ['mean', 'std'],
            'color_consistency': ['mean', 'std'],
            'avg_cmc': ['mean'],
            'creature_count': ['mean'],
            'evasion_score': ['mean'],
            'removal_score': ['mean'],
            'card_advantage_score': ['mean']
        }).round(2)

        print("\n\n--- ANALISI STATISTICA AGGREGATA ---")
        print(f"Basata su {len(df['draft_id'].unique())} draft completi.")
        print(summary)
        
        # Calcoliamo la percentuale di vittorie (il bot con il punteggio più alto in un draft)
        top_scores = df.loc[df.groupby('draft_id')['final_score'].idxmax()]
        win_counts = top_scores['bot_type'].value_counts(normalize=True) * 100
        
        print("\n--- Percentuale di volte con il punteggio più alto ---")
        print(win_counts.round(2).to_string())


def main():
    """Script principale per l'esecuzione della suite di valutazione."""
    print("--- Avvio Suite di Valutazione Robusta ---")

    # Carica i dati una sola volta
    card_database = load_json_file(CARD_DB_PATH)
    cube_list_data = load_json_file(CUBE_LIST_PATH)
    card_db_by_name = {card['name']: card for card in card_database}
    cube_card_names_set = set(cube_list_data['cards'])
    cube_full_details = [card for name, card in card_db_by_name.items() if name in cube_card_names_set]

    # Crea e avvia la suite di valutazione
    evaluation_suite = EvaluationSuite(cube_full_details, MODEL_PATH)
    evaluation_suite.run_all(NUM_SIMULATIONS)


if __name__ == "__main__":
    main()
