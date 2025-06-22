from typing import List, Dict
from collections import Counter
import numpy as np

from src.environment.draft import Card

def evaluate_deck(card_pool: List[Card]) -> Dict[str, float]:
    """
    Analizza un pool di 45 carte e restituisce un dizionario di metriche di base.
    """
    if not card_pool:
        return {"final_score": 0, "color_consistency": 0, "avg_cmc": 0, "creature_count": 0}

    # 1. Coerenza Colori
    color_identities = [set(card.details.get('color_identity', [])) for card in card_pool]
    all_colors_flat = [color for identity in color_identities if identity for color in identity]
    color_counts = Counter(all_colors_flat)
    main_colors = {color for color, count in color_counts.most_common(2)}
    num_main_color_cards = sum(1 for identity in color_identities if identity and identity.issubset(main_colors))
    color_consistency = (num_main_color_cards / len(card_pool)) * 100 if card_pool else 0

    # 2. Curva di Mana
    avg_cmc = np.mean([card.details.get('cmc', 0) for card in card_pool])

    # 3. Conteggio Creature
    num_creatures = sum(1 for card in card_pool if "Creature" in card.details.get('type_line', ''))
    
    # Punteggio Finale Semplificato: premia la coerenza e una curva bassa
    final_score = (color_consistency * 1.5) - (avg_cmc * 10) + num_creatures
    
    return {
        "final_score": round(final_score, 2),
        "color_consistency": round(color_consistency, 2),
        "avg_cmc": round(avg_cmc, 2),
        "creature_count": int(num_creatures)
    }
