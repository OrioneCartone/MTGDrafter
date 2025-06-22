from typing import List, Dict
from collections import Counter
import numpy as np

from src.environment.draft import Card
from src.features.cardencoders import CardEncoder
from src.utils.constants import KEYWORD_LIST, ABILITY_PATTERNS, OLD_FEATURE_SIZE

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
    
    # --- LOGICA CORRETTA RIPRISTINATA QUI ---
    main_colors = {color for color, count in color_counts.most_common(2)}
    num_main_color_cards = sum(1 for identity in color_identities if identity and identity.issubset(main_colors))
    color_consistency_score = (num_main_color_cards / len(card_pool)) * 100
    # --- FINE CORREZIONE ---

    avg_cmc = np.mean([card.details.get('cmc', 0) for card in card_pool])
    curve_score = max(0, 100 - 30 * abs(avg_cmc - 2.8))
    
    # Usiamo l'indice corretto per la creatura (è il sesto dopo i 5 colori e 1 cmc)
    # 0-4: colori, 5: cmc, 6: creatura
    num_creatures = np.sum(card_vectors[:, 6])
    creature_bonus = 30 if 15 <= num_creatures <= 20 else 0

    # --- 2. Metriche Basate su Feature Avanzate ---
    keyword_offset = OLD_FEATURE_SIZE
    ability_offset = OLD_FEATURE_SIZE + len(KEYWORD_LIST)

    keyword_counts = np.sum(card_vectors[:, keyword_offset : ability_offset], axis=0)
    ability_counts = np.sum(card_vectors[:, ability_offset :], axis=0)
    
    keyword_map = {name: count for name, count in zip(KEYWORD_LIST, keyword_counts)}
    ability_map = {name: count for name, count in zip(ABILITY_PATTERNS.keys(), ability_counts)}
    
    evasion_score = (keyword_map.get('Flying', 0) * 3) + (keyword_map.get('Menace', 0) * 1.5)
    combat_score = (keyword_map.get('Deathtouch', 0) * 2) + (keyword_map.get('First strike', 0) * 1.5) + (keyword_map.get('Double strike', 0) * 3)
    removal_score = (ability_map.get('destroy_creature', 0) * 4) + (ability_map.get('exile_permanent', 0) * 5)
    advantage_score = (ability_map.get('draw_multiple_cards', 0) * 5) + (ability_map.get('cantrip', 0) * 3)
    synergy_score = (ability_map.get('pump_all', 0) * 4) + (ability_map.get('sac_outlet', 0) * 2)

    # --- 3. Punteggio Finale Aggregato ---
    final_score = (
        color_consistency_score * 0.4 +
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
        "color_consistency": round(color_consistency_score, 2),
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
