from pathlib import Path
import sys
import json
from tqdm import tqdm

# --- BLOCCO DI CODICE EFFETTIVO ---
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))
# --- FINE BLOCCO ---

from src.environment.draftsimulator import DraftSimulator
from src.environment.opponents import ScoringBot
from src.environment.draft import Player
from src.training.logger import DraftLogger

# --- Configurazione ---
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = DATA_DIR / "processed" / "pauper_generalist_logs"
CARD_DB_PATH = DATA_DIR / "external" / "scryfall_commons.json"
CUBE_LISTS_DIR = DATA_DIR / "raw" / "cube_lists"

NUM_PLAYERS = 8
DRAFTS_PER_CUBE = 1

def load_json_file(path: Path):
    if not path.exists():
        print(f"ERRORE: Il file {path} non è stato trovato.")
        sys.exit(1)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    """Genera log di draft sintetici da TUTTI i cubi Pauper disponibili."""
    print("--- Preparazione Generazione Log (Pauper Generalist) ---")
    
    card_database = load_json_file(CARD_DB_PATH)
    card_db_by_name = {card['name']: card for card in card_database}
    
    logger = DraftLogger(output_dir=LOGS_DIR)

    cube_files = list(CUBE_LISTS_DIR.glob("*.json"))
    if not cube_files:
        print(f"ERRORE: Nessun file di cubo trovato in {CUBE_LISTS_DIR}.")
        sys.exit(1)

    print(f"Trovati {len(cube_files)} cubi. Generando {DRAFTS_PER_CUBE} log per ciascuno.")
    
    draft_id_counter = 0
    for cube_path in tqdm(cube_files, desc="Processando Cubi"):
        cube_list_data = load_json_file(cube_path)
        cube_card_names_set = set(cube_list_data['cards'])
        cube_full_details = [card for name, card in card_db_by_name.items() if name in cube_card_names_set]
        
        if len(cube_full_details) < NUM_PLAYERS * 45:
            print(f"ATTENZIONE: Salto il cubo {cube_path.name}, carte insufficienti.")
            continue
            
        for _ in tqdm(range(DRAFTS_PER_CUBE), desc=f"Drafting {cube_path.stem}", leave=False):
            bots = [ScoringBot(Player(player_id=j)) for j in range(NUM_PLAYERS)]
            cube_copy = list(cube_full_details)
            
            simulator = DraftSimulator(
                cube_list=cube_copy, bots=bots, draft_id=draft_id_counter, logger=logger
            )
            simulator.run_draft(verbose=False)
            draft_id_counter += 1

    total_logs = len(list(LOGS_DIR.glob("*.json")))
    print(f"\n✅ Generazione log completata. Creati {total_logs} file di log totali.")
    print(f"Controlla la cartella: {LOGS_DIR}")

if __name__ == "__main__":
    main()
