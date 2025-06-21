import json
from pathlib import Path
import sys
import re # Importiamo la libreria per le espressioni regolari

# Aggiunge la root del progetto al path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.environment.draftsimulator import DraftSimulator
from src.environment.opponents import RandomBot
from src.environment.draft import Player

# --- Configurazione ---
DATA_DIR = PROJECT_ROOT / "data"
CARD_DB_PATH = DATA_DIR / "external" / "scryfall_commons.json"
CUBE_LIST_PATH = DATA_DIR / "raw" / "cube_lists" / "thepaupercube.json"
NUM_PLAYERS = 8

def load_json_file(path: Path):
    """Carica un file JSON."""
    if not path.exists():
        print(f"ERRORE: Il file {path} non è stato trovato. Esegui prima 'scripts/download_data.py'.")
        sys.exit(1)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def normalize_card_name(name: str) -> str:
    """
    Normalizza il nome di una carta per un confronto affidabile.
    - Converte in minuscolo.
    - Rimuove spazi extra.
    - Rimuove tutto ciò che è tra parentesi (es. edizioni, note).
    """
    # Rimuove il contenuto tra parentesi, es. " (SLD)"
    name = re.sub(r'\s*\(.*\)\s*', '', name)
    # Converte in minuscolo e rimuove spazi iniziali/finali
    return name.lower().strip()

def main():
    """Script per eseguire una simulazione di draft completa."""
    print("--- Preparazione Simulazione Draft ---")

    # 1. Carica il database delle carte e la lista del cubo
    card_database = load_json_file(CARD_DB_PATH)
    cube_list_data = load_json_file(CUBE_LIST_PATH)
    
    # --- MODIFICA CHIAVE: CREA UN DIZIONARIO CON NOMI NORMALIZZATI ---
    print("Normalizzazione del database delle carte...")
    card_db_by_normalized_name = {
        normalize_card_name(card['name']): card for card in card_database
    }
    
    # 2. Filtra il database per avere solo le carte presenti nel nostro cubo
    print("Associazione delle carte del cubo con il database...")
    cube_card_names = cube_list_data['cards']
    cube_full_details = []
    not_found_count = 0

    for name in cube_card_names:
        normalized_name = normalize_card_name(name)
        if normalized_name in card_db_by_normalized_name:
            cube_full_details.append(card_db_by_normalized_name[normalized_name])
        else:
            # Aggiungiamo un print per vedere quali carte non trova, è utile per il debug
            # print(f"  -> Carta non trovata nel DB: '{name}' (normalizzata in '{normalized_name}')")
            not_found_count += 1
            
    print(f"Trovate {len(cube_full_details)}/{len(cube_card_names)} carte del cubo nel database.")
    if not_found_count > 0:
        print(f"ATTENZIONE: {not_found_count} carte non trovate. Potrebbero essere non-comuni o avere nomi particolari.")
    # --- FINE MODIFICA ---

    if len(cube_full_details) < 360:
        print(f"ERRORE CRITICO: Trovate solo {len(cube_full_details)} carte. Non abbastanza per un draft da {NUM_PLAYERS} giocatori.")
        sys.exit(1)

    # 3. Crea i giocatori e i bot
    bots = []
    for i in range(NUM_PLAYERS):
        player = Player(player_id=i)
        bot = RandomBot(player=player)
        bots.append(bot)
    print(f"Creati {len(bots)} RandomBot.")

    # 4. Inizializza e avvia il simulatore
    simulator = DraftSimulator(cube_list=cube_full_details, bots=bots, num_players=NUM_PLAYERS)
    final_pools = simulator.run_draft()

    # 5. Mostra i risultati
    print("\n--- RISULTATI DEL DRAFT ---")
    for player_id, player in final_pools.items():
        print(f"\n== Mazzo del Giocatore {player_id} ({len(player.pool)} carte) ==")
        card_names = sorted([card.name for card in player.pool])
        for i in range(0, len(card_names), 3):
             print("  |  ".join(card_names[i:i+3]))

if __name__ == "__main__":
    main()

