# File: src/features/card_encoders.py

import re
from typing import List, Dict

class CardEncoder:
    def __init__(self):
        self.color_order = ['W', 'U', 'B', 'R', 'G']
        self.type_order = ['Creature', 'Instant', 'Sorcery', 'Artifact', 'Enchantment', 'Land', 'Planeswalker']

    # QUESTA FUNZIONE DOVREBBE RESTITUIRE UN VETTORE DI LUNGHEZZA 5
    def _encode_colors(self, card_details: Dict) -> List[int]:
        colors = card_details.get('color_identity', [])
        return [1 if c in colors else 0 for c in self.color_order]

    # QUESTA FUNZIONE DOVREBBE RESTITUIRE UNA LISTA CON 1 ELEMENTO
    def _encode_cmc(self, card_details: Dict) -> List[float]:
        # --- POSSIBILE PUNTO DI ERRORE ---
        # Assicurati che il valore sia restituito all'interno di una lista, es: [2.0]
        return [card_details.get('cmc', 0.0)]

    # QUESTA FUNZIONE DOVREBBE RESTITUIRE UN VETTORE DI LUNGHEZZA 7
    def _encode_type(self, card_details: Dict) -> List[int]:
        type_line = card_details.get('type_line', '')
        return [1 if t in type_line else 0 for t in self.type_order]

    # QUESTA FUNZIONE DOVREBBE RESTITUIRE UNA LISTA CON 2 ELEMENTI
    def _encode_pt(self, card_details: Dict) -> List[int]:
        if 'power' in card_details:
            try:
                power = int(card_details['power'])
            except (ValueError, TypeError): # Gestisce '*' e None
                power = 0 
            try:
                toughness = int(card_details['toughness'])
            except (ValueError, TypeError):
                toughness = 0
            return [power, toughness]
        return [0, 0]

    # IL TOTALE DOVREBBE ESSERE 5 + 1 + 7 + 2 = 15
    def encode_card(self, card_details: Dict) -> List[float]:
        color_vec = self._encode_colors(card_details)
        cmc_vec = self._encode_cmc(card_details)
        type_vec = self._encode_type(card_details)
        pt_vec = self._encode_pt(card_details)
        
        # --- AGGIUNGIAMO UN PRINT DI DEBUG QUI PER VERIFICARE ---
        # print(f"Len: {len(color_vec)} (color) + {len(cmc_vec)} (cmc) + {len(type_vec)} (type) + {len(pt_vec)} (pt) = {len(color_vec+cmc_vec+type_vec+pt_vec)}")
        
        return color_vec + cmc_vec + type_vec + pt_vec
