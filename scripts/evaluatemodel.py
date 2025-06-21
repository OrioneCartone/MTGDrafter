from pathlib import Path
import sys
import json
import torch # Aggiungiamo torch per coerenza, anche se non usato direttamente qui


# Aggiunge la root del progetto al path di Python per trovare i nostri moduli
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))


from src.environment.draftsimulator import DraftSimulator
from src.environment.opponents import RandomBot, ScoringBot, AIBot
from src.environment.draft import Player
from src.utils.constants import FEATURE_SIZE # Ora questo import funzionerà

# --- Configurazione della Valutazione ---
DATA_DIR = PROJECT_ROOT / "data"
MODEL_PATH = PROJECT_ROOT / "models" / "experiments" / "run_01" / "policy_net_final.pth"
CARD_DB_PATH = DATA_DIR / "external" / "scryfall_commons.json"
CUBE_LIST_PATH = DATA_DIR / "raw" / "cube_lists" / "thepaupercube.json"

NUM_PLAYERS = 8

def load_json_file(path: Path):
    """Carica un file JSON e gestisce l'errore se non esiste."""
    if not path.exists():
        print(f"ERRORE: Il file {path} non è stato trovato.")
        print("Esegui prima 'scripts/download_data.py'.")
        sys.exit(1)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    """Script per valutare il modello AI in una simulazione di draft."""
    print("--- Avvio Script di Valutazione ---")

    # 1. Carica i dati necessari
    card_database = load_json_file(CARD_DB_PATH)
    cube_list_data = load_json_file(CUBE_LIST_PATH)
    card_db_by_name = {card['name']: card for card in card_database}
    cube_card_names = cube_list_data['cards']
    cube_full_details = [card_db_by_name[name] for name in cube_card_names if name in card_db_by_name]

    # 2. Crea i giocatori e i bot
    print("\n--- Configurazione del Tavolo di Draft ---")
    bots = []

    ai_player = Player(player_id=0)
    # Ora AIBot non ha più bisogno di feature_size come argomento
    ai_bot = AIBot(player=ai_player, model_path=MODEL_PATH)
    bots.append(ai_bot)

    for i in range(1, NUM_PLAYERS):
        player = Player(player_id=i)
        bot = ScoringBot(player=player) 
        bots.append(bot)
    print(f"Tavolo configurato: 1 AIBot vs {NUM_PLAYERS - 1} ScoringBot.")

    # 3. Inizializza e avvia il simulatore
    simulator = DraftSimulator(cube_list=cube_full_details, bots=bots, num_players=NUM_PLAYERS)
    final_pools = simulator.run_draft()

    # 4. Mostra e analizza i risultati
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
             print("    |  ".join(card_names[i:i+3]))

if __name__ == "__main__":
    main()
