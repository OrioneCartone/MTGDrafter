from pathlib import Path
import sys
import json
import torch
import numpy as np
from tqdm import tqdm
from typing import Dict, List
import random
from scipy.stats import ttest_ind # <-- Import per il test statistico

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

def main():
    """Esegue una valutazione statisticamente robusta del modello AI."""
    print("--- Avvio Script di Valutazione Statistica ---")
    paths_config = CONFIG['paths']
    sim_config = CONFIG['simulation']

    # Caricamento modello e DB carte
    model_dir = PROJECT_ROOT / paths_config['model_save_dir']
    model_path = max(model_dir.glob("*.pth"), key=lambda p: p.stat().st_mtime)
    print(f"Valutazione del modello: {model_path.name}")

    card_db_path = PROJECT_ROOT / paths_config['card_db_path']
    card_database = load_json_file(card_db_path)
    card_db_by_name = {card['name']: card for card in card_database}
    
    # 1. RACCOLTA DI TUTTI I CUBI VALIDI
    num_players = sim_config['num_players']
    cards_needed_for_draft = num_players * sim_config['num_packs'] * sim_config['pack_size']
    
    all_cubes_paths = list((PROJECT_ROOT / paths_config['cube_lists_dir']).glob("*.json"))
    valid_cubes: List[Dict] = []
    for cube_path in all_cubes_paths:
        cube_data = load_json_file(cube_path)
        cube_card_names = cube_data.get('cards', [])
        potential_cube = [Card(name=name, details=card_db_by_name[name]) for name in cube_card_names if name in card_db_by_name]
        if len(potential_cube) >= cards_needed_for_draft:
            valid_cubes.append({'name': cube_path.name, 'cards': potential_cube})

    if not valid_cubes:
        print(f"ERRORE: Nessun cubo valido trovato con almeno {cards_needed_for_draft} carte.")
        sys.exit(1)
    print(f"Trovati {len(valid_cubes)} cubi validi per la valutazione.")

    # 2. ESECUZIONE DELLE SIMULAZIONI
    drafts_per_cube = 50 # Aumenta questo valore per una maggiore robustezza (es. 50-100)
    total_drafts = len(valid_cubes) * drafts_per_cube
    print(f"Esecuzione di {drafts_per_cube} draft per cubo, per un totale di {total_drafts} simulazioni...")

    all_ai_scores, all_bot_scores = [], []
    
    with tqdm(total=total_drafts, desc="Valutazione Statistica") as progress_bar:
        for cube in valid_cubes:
            for _ in range(drafts_per_cube):
                # 2a. Randomizzazione della posizione del bot AI
                ai_seat = random.randint(0, num_players - 1)
                
                bots = []
                for i in range(num_players):
                    player = Player(player_id=i)
                    if i == ai_seat:
                        bots.append(AIBot(player, model_path))
                    else:
                        bots.append(ScoringBot(player))
                
                simulator = DraftSimulator(
                    cube_list=list(cube['cards']), bots=bots, num_players=num_players,
                    pack_size=sim_config['pack_size'], num_packs=sim_config['num_packs'],
                    draft_id=f"eval_{progress_bar.n}"
                )
                final_players = simulator.run_draft(verbose=False)
                
                # Raccogli i punteggi
                ai_score = evaluate_deck(final_players[ai_seat].pool)['final_score']
                bot_scores_in_draft = [evaluate_deck(p.pool)['final_score'] for i, p in final_players.items() if i != ai_seat]
                
                all_ai_scores.append(ai_score)
                all_bot_scores.extend(bot_scores_in_draft) # Aggiungi tutti i punteggi dei bot
                progress_bar.update(1)

    # 3. ANALISI STATISTICA DEI RISULTATI
    avg_ai_score = np.mean(all_ai_scores)
    avg_bot_score = np.mean(all_bot_scores)
    
    # Esegui il t-test per confrontare i due campioni di punteggi (AI vs. ScoringBot)
    # L'opzione 'equal_var=False' (Welch's t-test) è più robusta se le varianze sono diverse.
    t_stat, p_value = ttest_ind(all_ai_scores, all_bot_scores, equal_var=False, nan_policy='omit')

    print("\n\n--- Risultati Finali Valutazione Statistica ---")
    print(f"Totale Draft Simulati: {total_drafts}")
    print(f"Punteggio medio mazzo AI: {avg_ai_score:.2f} (StDev: {np.std(all_ai_scores):.2f})")
    print(f"Punteggio medio mazzo ScoringBot: {avg_bot_score:.2f} (StDev: {np.std(all_bot_scores):.2f})")
    print("-" * 40)
    print(f"Statistica T: {t_stat:.4f}")
    print(f"P-value: {p_value:.4f}")
    print("-" * 40)

    if p_value < 0.05:
        if avg_ai_score > avg_bot_score:
            print("CONCLUSIONE: La differenza è statisticamente significativa. Il modello AI è superiore allo ScoringBot.")
        else:
            print("CONCLUSIONE: La differenza è statisticamente significativa. Lo ScoringBot è superiore al modello AI.")
    else:
        print("CONCLUSIONE: La differenza non è statisticamente significativa. Non possiamo concludere che un bot sia superiore all'altro.")
    print("-------------------------------------------------")

if __name__ == '__main__':
    main()
