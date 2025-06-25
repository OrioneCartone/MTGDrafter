from pathlib import Path
import sys
import json
import torch
import numpy as np
from tqdm import tqdm
from typing import Dict, List
import random
from scipy.stats import ttest_ind

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

def print_deck_comparison(ai_player: Player, bot_player: Player):
    """Stampa una tabella comparativa dei mazzi finali."""
    print("\n" + "="*95)
    print("--- Confronto Mazzi (dall'ultimo draft eseguito) ---".center(95))
    print("="*95)
    
    ai_deck_names = sorted([card.name for card in ai_player.pool])
    bot_deck_names = sorted([card.name for card in bot_player.pool])
    
    max_len = max(len(ai_deck_names), len(bot_deck_names))
    
    ai_score_dict = evaluate_deck(ai_player.pool)
    bot_score_dict = evaluate_deck(bot_player.pool)
    
    # --- FIX 1: Correzione dell'errore di sintassi e logica ---
    # La riga 'header' è stata riscritta per essere sintatticamente corretta,
    # leggibile e per includere anche il punteggio del bot.
    ai_title = f"Mazzo dell'IA (Punteggio: {ai_score_dict['final_score']:.2f})"
    bot_title = f"Mazzo dello ScoringBot (Punteggio: {bot_score_dict['final_score']:.2f})"
    header = f"{ai_title:<45} | {bot_title:<45}"
    
    print(header)
    print("-" * len(header))
    
    for i in range(max_len):
        ai_card = ai_deck_names[i] if i < len(ai_deck_names) else ''
        bot_card = bot_deck_names[i] if i < len(bot_deck_names) else ''
        row = f"{ai_card:<45} | {bot_card:<45}"
        print(row)
    print("-" * len(header))

def main():
    """Esegue una valutazione statisticamente robusta del modello AI."""
    print("--- Avvio Script di Valutazione Statistica ---")
    
    paths_config = CONFIG['paths']
    sim_config = CONFIG['simulation']
    eval_config = CONFIG['evaluation']
    
    model_name = "model_final.pth"
    model_path = PROJECT_ROOT / paths_config['model_save_dir'] / model_name
    if not model_path.exists():
        print(f"ERRORE: Il modello '{model_name}' non è stato trovato in {model_path.parent}.")
        sys.exit(1)
    print(f"Valutazione del modello: {model_name}")

    card_db_path = PROJECT_ROOT / paths_config['card_db_path']
    card_database = load_json_file(card_db_path)
    card_db_by_name = {card['name']: card for card in card_database}
    
    cube_lists_dir = PROJECT_ROOT / paths_config['cube_lists_dir']
    all_cubes = list(cube_lists_dir.glob("*.json"))
    
    cards_needed_for_draft = sim_config['num_players'] * sim_config['num_packs'] * sim_config['pack_size']
    
    valid_cubes = []
    for cube_path in all_cubes:
        cube_data = load_json_file(cube_path)
        if len(cube_data.get('cards', [])) >= cards_needed_for_draft:
            valid_cubes.append(cube_path)

    if not valid_cubes:
        print(f"ERRORE: Nessun cubo valido trovato con almeno {cards_needed_for_draft} carte.")
        sys.exit(1)
    print(f"Trovati {len(valid_cubes)} cubi validi per la valutazione.")

    drafts_per_cube = eval_config['drafts_per_cube']
    total_drafts = len(valid_cubes) * drafts_per_cube
    print(f"Esecuzione di {drafts_per_cube} draft per cubo, per un totale di {total_drafts} simulazioni...")

    all_ai_scores, all_bot_scores = [], []
    last_draft_players = None

    with tqdm(total=total_drafts, desc="Valutazione Statistica") as progress_bar:
        for cube_path in valid_cubes:
            cube_data = load_json_file(cube_path)
            cube_card_names = cube_data.get('cards', [])
            cube_full_details = [Card(name=name, details=card_db_by_name[name]) for name in cube_card_names if name in card_db_by_name]
            
            for i in range(drafts_per_cube):
                players = [Player(player_id=j) for j in range(sim_config['num_players'])]
                bots = [AIBot(players[0], model_path)] + [ScoringBot(p) for p in players[1:]]
                
                simulator = DraftSimulator(
                    cube_list=cube_full_details,
                    bots=bots,
                    num_players=sim_config['num_players'],
                    pack_size=sim_config['pack_size'],
                    num_packs=sim_config['num_packs'],
                    draft_id=f"eval_{cube_path.stem}_{i}"
                )
                final_players_dict = simulator.run_draft(verbose=False)
                last_draft_players = final_players_dict

                ai_player = final_players_dict[0]
                bot_players = [final_players_dict[i] for i in range(1, sim_config['num_players'])]

                all_ai_scores.append(evaluate_deck(ai_player.pool)['final_score'])
                all_bot_scores.extend([evaluate_deck(p.pool)['final_score'] for p in bot_players])
                
                progress_bar.update(1)

    if last_draft_players:
        # Passa il secondo giocatore (ID 1) per il confronto
        print_deck_comparison(last_draft_players[0], last_draft_players[1])

    print("\n" + "="*95)
    print("--- Risultati Statistici della Valutazione ---".center(95))
    print("="*95)
    
    if not all_ai_scores:
        print("Nessun dato raccolto per la valutazione. Impossibile procedere.")
        return

    mean_ai_score = np.mean(all_ai_scores)
    mean_bot_score = np.mean(all_bot_scores)
    
    print(f"Punteggio medio mazzo IA      : {mean_ai_score:.2f} (Dev. Std: {np.std(all_ai_scores):.2f})")
    print(f"Punteggio medio mazzo ScoringBot: {mean_bot_score:.2f} (Dev. Std: {np.std(all_bot_scores):.2f})")
    
    if mean_ai_score > mean_bot_score:
        print("\n✅ L'IA ha ottenuto un punteggio medio SUPERIORE allo ScoringBot.")
    else:
        print("\n❌ L'IA ha ottenuto un punteggio medio INFERIORE o uguale allo ScoringBot.")
        
    if len(all_ai_scores) > 1 and len(all_bot_scores) > 1:
        t_stat, p_value = ttest_ind(all_ai_scores, all_bot_scores, equal_var=False, alternative='greater')
        print(f"\n--- Test di Significatività (T-test a una coda) ---")
        print(f"P-value: {p_value:.4f}")
        
        alpha = 0.05
        if p_value < alpha:
            print(f"Il risultato è statisticamente significativo (p < {alpha}). Si può affermare con alta confidenza che l'IA è superiore.")
        else:
            print(f"Il risultato NON è statisticamente significativo (p >= {alpha}). Non si può concludere che la differenza sia reale.")

# --- FIX 2: Correzione dell'errore logico ---
# Lo script ora chiama la funzione main() per essere eseguito.
if __name__ == '__main__':
    main()