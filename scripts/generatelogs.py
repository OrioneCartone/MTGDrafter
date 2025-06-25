from pathlib import Path
import sys
import json
from tqdm import tqdm

# --- BLOCCO DI CODICE EFFETTIVO ---
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.utils.config_loader import CONFIG
# MODIFICA: Aggiungi l'import mancante per la classe Player
from src.environment.draft import Card, Player
from src.environment.draftsimulator import DraftSimulator
from src.environment.opponents import ScoringBot
from src.training.logger import DraftLogger

# --- FINE BLOCCO ---

# --- MODIFICA 1: Importa la configurazione ---
# --- MODIFICA 2: I percorsi e i parametri sono ora presi dal file di configurazione ---
# --- Caricamento Configurazione ---
paths_config = CONFIG['paths']
sim_config = CONFIG['simulation']
# MODIFICA: Carica la sezione di configurazione specifica per la generazione dei log
log_gen_config = CONFIG['log_generation']

LOGS_DIR = PROJECT_ROOT / paths_config['log_output_dir']
CUBE_LISTS_DIR = PROJECT_ROOT / paths_config['cube_lists_dir']
CARD_DB_PATH = PROJECT_ROOT / paths_config['card_db_path']

NUM_PLAYERS = sim_config['num_players']
# MODIFICA: Leggi il parametro dalla sezione corretta
DRAFTS_PER_CUBE = log_gen_config['num_drafts_per_cube']

def load_json_file(path: Path):
    if not path.exists():
        print(f"ERRORE: Il file {path} non è stato trovato.")
        sys.exit(1)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    """Genera log di draft sintetici da TUTTI i cubi Pauper disponibili."""
    print("--- Preparazione Generazione Log (Pauper Generalist) ---")
    
    # Assicurati che la cartella dei log esista
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # MODIFICA: Usa 'log_dir' invece di 'output_dir'
    logger = DraftLogger(log_dir=LOGS_DIR)
    
    card_database = load_json_file(CARD_DB_PATH)
    card_db_by_name = {card['name']: card for card in card_database}
    
    all_cubes = list(CUBE_LISTS_DIR.glob("*.json"))
    draft_id_counter = 0
    
    # MODIFICA: Legge il numero di draft dal file di configurazione
    log_gen_config = CONFIG['log_generation']
    num_drafts_to_generate = log_gen_config['num_drafts_per_cube']
    print(f"Generazione di {num_drafts_to_generate} log per ogni cubo...")

    for cube_path in tqdm(all_cubes, desc="Processing Cubes"):
        cube_data = load_json_file(cube_path)
        # MODIFICA: Accedi alla chiave 'cards' per ottenere la lista dei nomi
        cube_card_names = cube_data.get('cards', []) 
        
        cube_full_details = [Card(name=name, details=card_db_by_name[name]) for name in cube_card_names if name in card_db_by_name]
        
        cards_needed = NUM_PLAYERS * sim_config['pack_size'] * sim_config['num_packs']
        if len(cube_full_details) < cards_needed:
            tqdm.write(f"Skipping {cube_path.name}, not enough cards.")
            continue
            
        for i in range(DRAFTS_PER_CUBE):
            draft_id_counter += 1
            bots = [ScoringBot(Player(player_id=j)) for j in range(NUM_PLAYERS)]
            cube_copy = list(cube_full_details)
            
            simulator = DraftSimulator(
                cube_list=cube_copy, 
                bots=bots, 
                num_players=NUM_PLAYERS,
                pack_size=sim_config['pack_size'],
                num_packs=sim_config['num_packs'],
                draft_id=draft_id_counter, 
                logger=logger
            )
            simulator.run_draft(verbose=False)
            draft_id_counter += 1

    total_logs = len(list(LOGS_DIR.glob("*.json")))
    print(f"\n✅ Generazione log completata. Creati {total_logs} file di log totali.")
    print(f"Controlla la cartella: {LOGS_DIR}")

if __name__ == "__main__":
    main()
