import re
from typing import List, Dict
from src.utils.constants import KEYWORD_LIST, ABILITY_PATTERNS

class CardEncoder:
    """
    Trasforma il JSON di una carta da Scryfall in un vettore numerico (features),
    includendo informazioni base, keyword e abilità testuali.
    """
    def __init__(self):
        self.color_order = ['W', 'U', 'B', 'R', 'G']
        self.type_order = ['Creature', 'Instant', 'Sorcery', 'Artifact', 'Enchantment', 'Land', 'Planeswalker']

    # --- METODI BASE (CHE MANCAVANO) ---
    def _encode_colors(self, card_details: Dict) -> List[int]:
        colors = card_details.get('color_identity', [])
        return [1 if c in colors else 0 for c in self.color_order]

    def _encode_cmc(self, card_details: Dict) -> List[float]:
        return [card_details.get('cmc', 0.0)]

    def _encode_type(self, card_details: Dict) -> List[int]:
        type_line = card_details.get('type_line', '')
        return [1 if t in type_line else 0 for t in self.type_order]

    def _encode_pt(self, card_details: Dict) -> List[int]:
        if 'power' in card_details:
            try:
                power = int(card_details.get('power', 0))
            except (ValueError, TypeError):
                power = 0 
            try:
                toughness = int(card_details.get('toughness', 0))
            except (ValueError, TypeError):
                toughness = 0
            return [power, toughness]
        return [0, 0]

    # --- NUOVI METODI (GIÀ PRESENTI) ---
    def _encode_keywords(self, card_details: Dict) -> List[int]:
        """Crea un vettore one-hot per le keyword ufficiali."""
        keywords = card_details.get('keywords', [])
        keywords_lower = {k.lower() for k in keywords}
        keyword_list_lower = [k.lower() for k in KEYWORD_LIST]
        return [1 if k in keywords_lower else 0 for k in keyword_list_lower]

    def _encode_abilities(self, card_details: Dict) -> List[int]:
        """Crea un vettore one-hot cercando pattern nel testo oracolo."""
        oracle_text = card_details.get('oracle_text', '').lower()
        ability_vector = []
        for _, patterns in ABILITY_PATTERNS.items():
            # Un'abilità è presente se TUTTI i suoi pattern sono nel testo
            if all(p.lower() in oracle_text for p in patterns):
                ability_vector.append(1)
            else:
                ability_vector.append(0)
        return ability_vector

    # --- METODO PRINCIPALE CHE UNISCE TUTTO ---
    def encode_card(self, card_details: Dict) -> List[float]:
        """
        Esegue tutti i passaggi di encoding e restituisce un singolo vettore di feature.
        """
        # Feature base
        color_vec = self._encode_colors(card_details)
        cmc_vec = self._encode_cmc(card_details)
        type_vec = self._encode_type(card_details)
        pt_vec = self._encode_pt(card_details)
        
        # Nuove feature
        keyword_vec = self._encode_keywords(card_details)
        ability_vec = self._encode_abilities(card_details)
        
        # Uniamo tutto insieme
        return color_vec + cmc_vec + type_vec + pt_vec + keyword_vec + ability_vec

