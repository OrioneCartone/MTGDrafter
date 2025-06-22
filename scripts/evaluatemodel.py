from pathlib import Path
import sys
import json
import torch
import random
import time

# Aggiunge la root del progetto al path di Python per trovare i nostri moduli
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

# Importa tutti i moduli necessari dal nostro progetto
from src.environment.draftsimulator import DraftSimulator
from src.environment.opponents import ScoringBot, AIBot
from src.environment.draft import Player
from src.utils.constants import FEATURE_SIZE
from src.evaluation.evaluator import evaluate_deck

# --- Configurazione della Valutazione ---
DATA_DIR = PROJECT_ROOT / "data"
# Assicurati che questo percorso punti al modello corretto che vuoi valutare
MODEL_PATH = PROJECT_ROOT / "models" / "experiments" / "pauper_generalist_v1" / "policy_net_final.pth"
CARD_DB_PATH = DATA_DIR / "external" / "scryfall_commons.json"
# Usiamo 'thepaupercube' come nostro ambiente di test standard
CUBE_LIST_PATH = DATA_DIR / "raw" / "cube_lists" / "thepaupercube.json"

NUM_PLAYERS = 8

def load_json_file(path: Path):
    """Carica un file JSON e gestisce l'errore se non esiste."""
    if not path.exists():
        print(f"ERRORE: Il file {path} non è stato trovato.")
        sys.exit(1)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    """Valuta il modello AI in una simulazione di draft."""
    
    # --- Inizializza il Seed per un draft sempre diverso ---
    seed = int(time.time() * 1000)
    random.seed(seed)
    print(f"--- Avvio Script di Valutazione (Seed: {seed}) ---")
    
    # 1. Carica i dati necessari
    card_database = load_json_file(CARD_DB_PATH)
    cube_list_data = load_json_file(CUBE_LIST_PATH)
    card_db_by_name = {card['name']: card for card in card_database}
    cube_card_names_set = set(cube_list_data['cards'])
    cube_full_details = [card for name, card in card_db_by_name.items() if name in cube_card_names_set]

    # 2. Crea i giocatori e i bot
    print("\n--- Configurazione del Tavolo di Draft ---")
    bots = []

    ai_player = Player(player_id=0)
    ai_bot = AIBot(player=ai_player, model_path=MODEL_PATH)
    bots.append(ai_bot)

    for i in range(1, NUM_PLAYERS):
        player = Player(player_id=i)
        bot = ScoringBot(player=player) 
        bots.append(bot)
    print(f"Tavolo configurato: 1 AIBot (Generalist) vs {NUM_PLAYERS - 1} ScoringBot.")
    print(f"Ambiente di test: {CUBE_LIST_PATH.name}")

    # 3. Inizializza e avvia il simulatore
    simulator = DraftSimulator(cube_list=cube_full_details, bots=bots)
    final_pools = simulator.run_draft(verbose=True)

    # 4. Mostra e analizza i risultati con punteggi
    print("\n--- RISULTATI E PUNTEGGI DEI MAZZI ---")
    
    for player_id, player in final_pools.items():
        bot_type = "AI" if player_id == 0 else "Scoring"
        deck_metrics = evaluate_deck(player.pool)
        
        print(f"\n== Mazzo del Giocatore {player_id} ({bot_type}) - PUNTEGGIO FINALE: {deck_metrics['final_score']} ==")
        print(f"  Metriche Base: Coerenza: {deck_metrics['color_consistency']}% | CMC Medio: {deck_metrics['avg_cmc']} | Creature: {deck_metrics['creature_count']}")
        
        # Stampa i punteggi parziali
        raw_scores = deck_metrics['raw_scores']
        print(f"  Punteggi Sinergia: Evasione: {raw_scores['evasion']} | Combattimento: {raw_scores['combat']} | Rimozioni: {raw_scores['removal']} | Vant. Carte: {raw_scores['advantage']}")
if __name__ == "__main__":
    main()
