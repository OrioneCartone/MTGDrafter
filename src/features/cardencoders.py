# src/features/cardencoders.py
import re
from typing import List, Dict

class CardEncoder:
    def __init__(self):
        self.color_order = ['W', 'U', 'B', 'R', 'G']
        # Includiamo Planeswalker per una feature_size di 15, per massima compatibilità
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

    def encode_card(self, card_details: Dict) -> List[float]:
        color_vec = self._encode_colors(card_details)
        cmc_vec = self._encode_cmc(card_details)
        type_vec = self._encode_type(card_details)
        pt_vec = self._encode_pt(card_details)
        # 5 + 1 + 7 + 2 = 15
        return color_vec + cmc_vec + type_vec + pt_vec
