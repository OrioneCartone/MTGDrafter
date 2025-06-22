from typing import List, Dict
from collections import Counter
import numpy as np

from src.environment.draft import Card
from src.features.cardencoders import CardEncoder
from src.utils.constants import KEYWORD_LIST, ABILITY_PATTERNS, OLD_FEATURE_SIZE

# Creiamo i dizionari di mappatura a livello di modulo, così non vengono ricreati ogni volta
KEYWORD_INDICES = {name.lower(): i for i, name in enumerate(KEYWORD_LIST)}
ABILITY_INDICES = {name: i for i, name in enumerate(ABILITY_PATTERNS.keys())}
KEYWORD_OFFSET = OLD_FEATURE_SIZE
ABILITY_OFFSET = OLD_FEATURE_SIZE + len(KEYWORD_LIST)

def get_feature_value(vec: np.ndarray, feature_type: str, feature_name: str) -> int:
    """Helper per ottenere il valore di una feature da un vettore usando i nomi."""
    if feature_type == 'keyword':
        idx = KEYWORD_OFFSET + KEYWORD_INDICES.get(feature_name.lower(), -1)
    elif feature_type == 'ability':
        idx = ABILITY_OFFSET + ABILITY_INDICES.get(feature_name, -1)
    else:
        return 0
    
    if 0 <= idx < len(vec):
        return int(vec[idx])
    return 0


def evaluate_deck(card_pool: List[Card]) -> Dict[str, float]:
    """
    Analizza un pool di 45 carte usando metriche avanzate e restituisce un punteggio.
    """
    if not card_pool:
        return {"final_score": 0}

    encoder = CardEncoder()
    card_vectors = np.array([encoder.encode_card(card.details) for card in card_pool])
    
    # --- 1. Metriche Strutturali ---
    color_identities = [set(card.details.get('color_identity', [])) for card in card_pool]
    all_colors_flat = [color for identity in color_identities if identity for color in identity]
    color_counts = Counter(all_colors_flat)
    main_colors = {color for color, count in color_counts.most_common(2)}
    
    num_main_color_cards = sum(1 for identity in color_identities if identity and identity.issubset(main_colors))
    color_consistency = (num_main_color_cards / len(card_pool)) * 100

    avg_cmc = np.mean([card.details.get('cmc', 0) for card in card_pool])
    curve_score = max(0, 100 - 30 * abs(avg_cmc - 2.8))
    
    num_creatures = np.sum(card_vectors[:, 6]) # Indice di 'Is Creature' è 6
    creature_bonus = 30 if 15 <= num_creatures <= 20 else 0

    # --- 2. Metriche Avanzate ---
    evasion_score = 0
    combat_score = 0
    removal_score = 0
    advantage_score = 0
    synergy_score = 0
    
    # Calcoliamo i punteggi sommando i contributi di ogni carta
    for vec in card_vectors:
        evasion_score += get_feature_value(vec, 'keyword', 'Flying') * 3.0
        evasion_score += get_feature_value(vec, 'keyword', 'Menace') * 1.5
        
        combat_score += get_feature_value(vec, 'keyword', 'Deathtouch') * 2.0
        combat_score += get_feature_value(vec, 'keyword', 'First strike') * 1.5
        
        removal_score += get_feature_value(vec, 'ability', 'destroy_creature') * 4.0
        removal_score += get_feature_value(vec, 'ability', 'exile_permanent') * 5.0
        removal_score += get_feature_value(vec, 'ability', 'counter_spell') * 4.0
        
        advantage_score += get_feature_value(vec, 'ability', 'draw_multiple_cards') * 5.0
        advantage_score += get_feature_value(vec, 'ability', 'cantrip') * 3.0
        
        synergy_score += get_feature_value(vec, 'ability', 'pump_all') * 4.0

    # --- 3. Punteggio Finale ---
    final_score = (
        color_consistency * 0.4 +
        curve_score * 0.2 +
        creature_bonus +
        evasion_score * 0.8 +
        combat_score * 0.6 +
        removal_score * 1.0 +
        advantage_score * 0.9 +
        synergy_score * 0.7
    )

    return {
        "final_score": round(final_score, 2),
        "color_consistency": round(color_consistency, 2),
        "avg_cmc": round(avg_cmc, 2),
        "creature_count": int(num_creatures),
        "raw_scores": {
            "evasion": round(evasion_score, 2),
            "combat": round(combat_score, 2),
            "removal": round(removal_score, 2),
            "advantage": round(advantage_score, 2),
            "synergy": round(synergy_score, 2)
        }
    }
