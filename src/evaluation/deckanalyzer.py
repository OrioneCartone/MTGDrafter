from typing import List, Dict
from collections import Counter
import numpy as np

from src.environment.draft import Card
from src.features.cardencoders import CardEncoder
from src.utils.constants import KEYWORD_LIST, ABILITY_PATTERNS, BASE_FEATURE_SIZE

# Helper per decodificare le feature all'interno di questo modulo,
# replicando la logica di ScoringBot per coerenza.
def _get_feature_from_vec(vec: List[float], f_type: str, f_name: str) -> int:
    keyword_indices = {name.lower(): i for i, name in enumerate(KEYWORD_LIST)}
    ability_indices = {name: i for i, name in enumerate(ABILITY_PATTERNS.keys())}
    keyword_offset = BASE_FEATURE_SIZE
    ability_offset = BASE_FEATURE_SIZE + len(KEYWORD_LIST)
    try:
        if f_type == 'keyword':
            idx = keyword_offset + keyword_indices[f_name.lower()]
        elif f_type == 'ability':
            idx = ability_offset + ability_indices[f_name]
        else: return 0
        if 0 <= idx < len(vec): return int(vec[idx])
        return 0
    except KeyError:
        return 0

def evaluate_deck(card_pool: List[Card]) -> Dict[str, float]:
    """
    Analizza un pool di carte, simula la costruzione di un mazzo da 40 carte (23+17)
    e restituisce metriche di qualità su quel mazzo.
    """
    if not card_pool or len(card_pool) < 23:
        return {"final_score": 0, "avg_cmc": 99, "creature_count": 0, "threat_density": 0, "answer_density": 0, "mana_consistency": 0}

    # FASE 1: Simulare la costruzione del mazzo
    color_counts = Counter(c for card in card_pool for c in card.details.get('colors', []))
    main_colors = {color for color, count in color_counts.most_common(2)}

    playables = [card for card in card_pool if not card.details.get('colors') or set(card.details.get('colors')).issubset(main_colors)]
    playables.sort(key=lambda c: (-len(c.details.get('colors', [])), c.details.get('cmc', 99)))
    deck_cards = playables[:23]

    if not deck_cards:
        return {"final_score": 0, "avg_cmc": 99, "creature_count": 0, "threat_density": 0, "answer_density": 0, "mana_consistency": 0}

    # FASE 2: Calcolare le metriche sul mazzo costruito
    encoder = CardEncoder()
    creature_count = sum(1 for c in deck_cards if "Creature" in c.details.get('type_line', ''))
    threat_density = (creature_count / 23) * 100

    answer_count = 0
    for card in deck_cards:
        features = encoder.encode_card(card.details)
        if _get_feature_from_vec(features, 'ability', 'destroy_creature') > 0 or \
           _get_feature_from_vec(features, 'ability', 'exile_permanent') > 0 or \
           _get_feature_from_vec(features, 'ability', 'board_wipe_damage') > 0 or \
           _get_feature_from_vec(features, 'ability', 'counter_spell_hard') > 0:
            answer_count += 1
    answer_density = (answer_count / 23) * 100

    cmc_list = [c.details.get('cmc', 0) for c in deck_cards if c.details.get('cmc', 0) > 0]
    avg_cmc = np.mean(cmc_list) if cmc_list else 0
    curve_consistency = 1 / (1 + np.std(cmc_list)) if cmc_list else 0

    mana_symbols = Counter(s for c in deck_cards for s in c.details.get('mana_cost', '') if s in "WUBRG")
    total_symbols = sum(mana_symbols.values())
    mana_consistency = sum(mana_symbols[c] for c in main_colors) / total_symbols if total_symbols > 0 else 0

    # FASE 3: Punteggio Finale Pesato
    final_score = ((threat_density * 0.3) + (answer_density * 0.5) + (curve_consistency * 15) + (mana_consistency * 25) - (avg_cmc * 2))

    return {
        "final_score": round(final_score, 2), "avg_cmc": round(avg_cmc, 2),
        "creature_count": int(creature_count), "threat_density": round(threat_density, 2),
        "answer_density": round(answer_density, 2), "mana_consistency": round(mana_consistency * 100, 2)
    }