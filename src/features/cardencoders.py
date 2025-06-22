# src/features/cardencoders.py
import re
from typing import List, Dict
from src.utils.constants import KEYWORD_LIST, ABILITY_PATTERNS

class CardEncoder:
    """
    Trasforma il JSON di una carta da Scryfall in un vettore numerico (features),
    includendo informazioni base, keyword e abilità testuali e strutturali.
    """
    def __init__(self):
        self.color_order = ['W', 'U', 'B', 'R', 'G']
        self.type_order = ['Creature', 'Instant', 'Sorcery', 'Artifact', 'Enchantment', 'Land', 'Planeswalker']

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
            try: power = int(card_details.get('power', 0))
            except (ValueError, TypeError): power = 0 
            try: toughness = int(card_details.get('toughness', 0))
            except (ValueError, TypeError): toughness = 0
            return [power, toughness]
        return [0, 0]

    def _encode_keywords(self, card_details: Dict) -> List[int]:
        keywords = card_details.get('keywords', [])
        keywords_lower = {k.lower() for k in keywords}
        keyword_list_lower = [k.lower() for k in KEYWORD_LIST]
        return [1 if k in keywords_lower else 0 for k in keyword_list_lower]

    def _encode_abilities(self, card_details: Dict) -> List[int]:
        """
        Crea un vettore one-hot per abilità testuali E strutturali,
        iterando sulla lista da constants.py.
        """
        oracle_text = card_details.get('oracle_text', '').lower()
        ability_vector = []

        for ability_name, patterns in ABILITY_PATTERNS.items():
            is_present = 0
            # --- Logica Speciale per Tipi Strutturali ---
            if ability_name == 'has_activated_ability_tap':
                if ':' in oracle_text and '{t}' in oracle_text.split(':', 1)[0]:
                    is_present = 1
            elif ability_name == 'has_activated_ability_mana':
                if ':' in oracle_text:
                    cost = oracle_text.split(':', 1)[0]
                    if any(mc in cost for mc in ['{w}','{u}','{b}','{r}','{g}','{c}','{x}']):
                        is_present = 1
            elif ability_name == 'has_triggered_ability':
                if oracle_text.startswith(('when', 'whenever', 'at')):
                    is_present = 1
            elif ability_name == 'has_static_anthem':
                 if 'creatures you control get +1/+1' in oracle_text:
                    is_present = 1
            # --- Logica Normale per Pattern di Testo ---
            else:
                if patterns and all(p.lower() in oracle_text for p in patterns):
                    is_present = 1
            
            ability_vector.append(is_present)
            
        return ability_vector

    def encode_card(self, card_details: Dict) -> List[float]:
        """Esegue tutti i passaggi di encoding e restituisce un singolo vettore di feature."""
        base_vec = (self._encode_colors(card_details) + 
                    self._encode_cmc(card_details) + 
                    self._encode_type(card_details) + 
                    self._encode_pt(card_details))
        
        keyword_vec = self._encode_keywords(card_details)
        ability_vec = self._encode_abilities(card_details)
        
        # Uniamo tutto insieme. Non c'è più una chiamata a _encode_ability_structures
        return base_vec + keyword_vec + ability_vec
