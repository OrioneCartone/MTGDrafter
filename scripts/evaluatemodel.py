from pathlib import Path
import sys
import json
import torch

# --- BLOCCO DI CODICE EFFETTIVO ---
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))
# --- FINE BLOCCO ---

from src.environment.draftsimulator import DraftSimulator
from src.environment.opponents import ScoringBot, AIBot
from src.environment.draft import Player
from src.utils.constants import FEATURE_SIZE

# --- Configurazione ---
DATA_DIR = PROJECT_ROOT / "data"
MODEL_PATH = PROJECT_ROOT / "models" / "experiments" / "pauper_generalist_v1" / "policy_net_final.pth"
CARD_DB_PATH = DATA_DIR / "external" / "scryfall_commons.json"
CUBE_LIST_PATH = DATA_DIR / "raw" / "cube_lists" / "thepaupercube.json"

NUM_PLAYERS = 8

def load_json_file(path: Path):
    if not path.exists():
        print(f"ERRORE: Il file {path} non è stato trovato.")
        sys.exit(1)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    """Valuta il modello Pauper Generalist in una simulazione di draft."""
    print("--- Avvio Script di Valutazione (Pauper Generalist) ---")

    card_database = load_json_file(CARD_DB_PATH)
    cube_list_data = load_json_file(CUBE_LIST_PATH)
    card_db_by_name = {card['name']: card for card in card_database}
    cube_card_names_set = set(cube_list_data['cards'])
    cube_full_details = [card for name, card in card_db_by_name.items() if name in cube_card_names_set]

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

    simulator = DraftSimulator(cube_list=cube_full_details, bots=bots)
    final_pools = simulator.run_draft(verbose=True)

    print("\n--- RISULTATI DELLA VALUTAZIONE ---")
    for player_id, player in final_pools.items():
        bot_type = "AI" if player_id == 0 else "Scoring"
        print(f"\n== Mazzo del Giocatore {player_id} ({bot_type}) ({len(player.pool)} carte) ==")
        
        color_counts = {'W': 0, 'U': 0, 'B': 0, 'R': 0, 'G': 0, 'C': 0}
        for card in player.pool:
            identity = card.details.get('color_identity', [])
            if not identity:
                color_counts['C'] += 1
            else:
                for color in identity:
                    color_counts[color] += 1
        
        print(f"  Distribuzione Colori: {color_counts}")
        card_names = sorted([card.name for card in player.pool])
        for i in range(0, len(card_names), 3):
             print(f"    {' | '.join(card_names[i:i+3])}")

if __name__ == "__main__":
    main()
