import re
from typing import List, Dict

class CardEncoder:
    """
    Trasforma il JSON di una carta da Scryfall in un vettore numerico (features).
    """
    def __init__(self):
        # Definiamo l'ordine dei colori e dei tipi per coerenza
        self.color_order = ['W', 'U', 'B', 'R', 'G']
        self.type_order = ['Creature', 'Instant', 'Sorcery', 'Artifact', 'Enchantment', 'Land']

    def _encode_colors(self, card_details: Dict) -> List[int]:
        """Crea un vettore di 5 elementi per l'identità di colore."""
        colors = card_details.get('color_identity', [])
        return [1 if c in colors else 0 for c in self.color_order]

    def _encode_cmc(self, card_details: Dict) -> List[float]:
        """Restituisce il costo di mana convertito (CMC)."""
        return [card_details.get('cmc', 0.0)]

    def _encode_type(self, card_details: Dict) -> List[int]:
        """Crea un vettore one-hot per il tipo di carta principale."""
        type_line = card_details.get('type_line', '')
        return [1 if t in type_line else 0 for t in self.type_order]

    def _encode_pt(self, card_details: Dict) -> List[int]:
        """Codifica forza e costituzione. Restituisce [0, 0] per le non-creature."""
        if 'power' in card_details:
            try:
                power = int(card_details['power'])
            except ValueError: # Gestisce i casi di P/T come '*'
                power = 0 
            try:
                toughness = int(card_details['toughness'])
            except ValueError:
                toughness = 0
            return [power, toughness]
        return [0, 0]

    def encode_card(self, card_details: Dict) -> List[float]:
        """
        Esegue tutti i passaggi di encoding e restituisce un singolo vettore di feature.
        """
        # Eseguiamo ogni funzione di encoding
        color_vec = self._encode_colors(card_details)
        cmc_vec = self._encode_cmc(card_details)
        type_vec = self._encode_type(card_details)
        pt_vec = self._encode_pt(card_details)
        
        # Uniamo tutti i vettori in un unico, grande vettore di feature
        # La lunghezza totale sarà 5 (colori) + 1 (cmc) + 7 (tipi) + 2 (p/t) = 15
        return color_vec + cmc_vec + type_vec + pt_vec

