import json
from pathlib import Path
import sys
from tqdm import tqdm # Aggiungiamo una barra di progresso!

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.environment.draftsimulator import DraftSimulator
from src.environment.opponents import ScoringBot
from src.environment.draft import Player
from src.training.logger import DraftLogger

# --- Configurazione ---
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = DATA_DIR / "processed" / "draft_logs"
CARD_DB_PATH = DATA_DIR / "external" / "scryfall_commons.json"
CUBE_LIST_PATH = DATA_DIR / "raw" / "cube_lists" / "thepaupercube.json"

NUM_PLAYERS = 8
NUM_DRAFTS_TO_GENERATE = 50 # Generiamo un numero più sostanzioso

def load_json_file(path: Path):
    if not path.exists():
        print(f"ERRORE: Il file {path} non è stato trovato. Esegui prima 'scripts/download_data.py'.")
        sys.exit(1)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    """Script principale per generare log di draft sintetici."""
    print("--- Preparazione Generazione Log ---")
    
    # Carica i dati una sola volta
    card_database = load_json_file(CARD_DB_PATH)
    cube_list_data = load_json_file(CUBE_LIST_PATH)
    card_db_by_name = {card['name']: card for card in card_database}
    cube_card_names = cube_list_data['cards']
    # Semplifichiamo la normalizzazione (già fatta in simulate_draft)
    cube_full_details = [card_db_by_name[name] for name in cube_card_names if name in card_db_by_name]

    # Inizializza il logger
    logger = DraftLogger(output_dir=LOGS_DIR)

    print(f"\n--- Avvio generazione di {NUM_DRAFTS_TO_GENERATE} draft logs ---")
    
    # Usiamo tqdm per una bella barra di progresso
    for i in tqdm(range(NUM_DRAFTS_TO_GENERATE), desc="Generando Drafts"):
        # Crea i bot per questo draft
        bots = [ScoringBot(Player(player_id=j)) for j in range(NUM_PLAYERS)]
        
        # Crea una copia del cubo per ogni simulazione, così non si esaurisce
        cube_copy = list(cube_full_details)
        
        # Inizializza il simulatore con il logger
        simulator = DraftSimulator(
            cube_list=cube_copy, 
            bots=bots, 
            draft_id=i,
            logger=logger
        )
        # Esegui il draft (non ci interessa il risultato finale, solo il logging)
        simulator.run_draft()

    print(f"\n✅ Generazione log completata. {NUM_DRAFTS_TO_GENERATE * NUM_PLAYERS * 45} pick sono stati loggati.")
    print(f"Controlla la cartella: {LOGS_DIR}")

if __name__ == "__main__":
    main()
