from pathlib import Path
import sys
import json
import torch
import numpy as np
from tqdm import tqdm
from typing import Dict

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.utils.config_loader import CONFIG
from src.environment.draft import Card, Player
from src.environment.draftsimulator import DraftSimulator
from src.environment.opponents import AIBot, ScoringBot
from src.evaluation.deckanalyzer import evaluate_deck

def load_json_file(path: Path):
    if not path.exists():
        print(f"ERRORE: Il file {path} non è stato trovato.")
        sys.exit(1)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def print_decks_table(final_players: Dict[int, Player], draft_num: int):
    """Stampa i mazzi dei primi 4 giocatori in una tabella comparativa."""
    player_ids_to_show = sorted(final_players.keys())[:4]
    
    decks, headers = [], []
    for pid in player_ids_to_show:
        player = final_players[pid]
        player_type = "AI Bot" if pid == 0 else "Scoring Bot"
        headers.append(f"{player_type} (P{pid})")
        
        sorted_pool = sorted(player.pool, key=lambda c: (c.details.get('cmc', 99), c.name))
        decks.append([c.name for c in sorted_pool])

    max_rows = max(len(deck) for deck in decks) if decks else 0
    col_width = 30
    
    # Stampa l'intestazione della tabella
    print(f"\n\n===== Risultati Draft di Valutazione #{draft_num} =====")
    header_line = "|"
    separator_line = "+"
    for header in headers:
        header_line += f" {header.center(col_width-2)} |"
        separator_line += "-" * col_width + "+"
    print(separator_line)
    print(header_line)
    print(separator_line)

    # Stampa le righe con le carte
    for i in range(max_rows):
        row_line = "|"
        for deck in decks:
            card_name = deck[i] if i < len(deck) else ""
            row_line += f" {card_name:<{col_width-2}} |"
        print(row_line)
    
    print(separator_line)

def main():
    """Valuta il modello AI addestrato e stampa i mazzi risultanti in una tabella."""
    print("--- Avvio Script di Valutazione Modello ---")
    paths_config = CONFIG['paths']
    sim_config = CONFIG['simulation']

    model_dir = PROJECT_ROOT / paths_config['model_save_dir']
    model_files = list(model_dir.glob("*.pth"))
    if not model_files:
        print(f"ERRORE: Nessun modello trovato in {model_dir}. Esegui prima l'addestramento.")
        sys.exit(1)
    model_path = max(model_files, key=lambda p: p.stat().st_mtime)
    print(f"Valutazione del modello più recente: {model_path.name}")

    card_db_path = PROJECT_ROOT / paths_config['card_db_path']
    cube_lists_dir = PROJECT_ROOT / paths_config['cube_lists_dir']
    card_database = load_json_file(card_db_path)
    card_db_by_name = {card['name']: card for card in card_database}
    
    num_players = sim_config['num_players']
    cards_needed_for_draft = num_players * sim_config['num_packs'] * sim_config['pack_size']
    
    all_cubes = list(cube_lists_dir.glob("*.json"))
    chosen_cube_path = None
    cube_full_details = []

    for cube_path in all_cubes:
        cube_data = load_json_file(cube_path)
        cube_card_names = cube_data.get('cards', [])
        potential_cube = [Card(name=name, details=card_db_by_name[name]) for name in cube_card_names if name in card_db_by_name]
        if len(potential_cube) >= cards_needed_for_draft:
            chosen_cube_path = cube_path
            cube_full_details = potential_cube
            break

    if not chosen_cube_path:
        print(f"ERRORE: Nessun cubo trovato in {cube_lists_dir} con abbastanza carte ({cards_needed_for_draft} necessarie).")
        sys.exit(1)
    
    print(f"Uso il cubo: {chosen_cube_path.name} ({len(cube_full_details)} carte valide)")

    ai_scores, bot_scores = [], []
    num_eval_drafts = 20
    print(f"Esecuzione di {num_eval_drafts} draft di valutazione (Pod da {num_players} giocatori)...")

    for i in tqdm(range(num_eval_drafts), desc="Valutazione Drafts"):
        ai_player = Player(player_id=0)
        bots = [AIBot(ai_player, model_path)]
        bots += [ScoringBot(Player(player_id=j)) for j in range(1, num_players)]
        
        simulator = DraftSimulator(
            cube_list=list(cube_full_details),
            bots=bots, 
            num_players=num_players,
            pack_size=sim_config['pack_size'], 
            num_packs=sim_config['num_packs'], 
            draft_id=f"eval_{i}"
        )
        final_players = simulator.run_draft(verbose=False)
        
        ai_deck_metrics = evaluate_deck(final_players[0].pool)
        ai_scores.append(ai_deck_metrics['final_score'])
        
        current_bot_scores = [evaluate_deck(final_players[j].pool)['final_score'] for j in range(1, num_players)]
        bot_scores.append(np.mean(current_bot_scores) if current_bot_scores else 0)

        # --- MODIFICA: Stampa i mazzi in una tabella ---
        print_decks_table(final_players, draft_num=i+1)

    avg_ai_score = np.mean(ai_scores)
    avg_bot_score = np.mean(bot_scores)
    win_rate = sum(1 for i in range(len(ai_scores)) if ai_scores[i] > bot_scores[i]) / len(ai_scores) if ai_scores else 0

    print("\n\n--- Risultati Finali Valutazione ---")
    print(f"Punteggio medio mazzo AI: {avg_ai_score:.2f}")
    print(f"Punteggio medio mazzo ScoringBot: {avg_bot_score:.2f}")
    print(f"Tasso di vittoria dell'AI (punteggio mazzo superiore): {win_rate:.2%}")
    print("------------------------------------")

if __name__ == '__main__':
    main()
