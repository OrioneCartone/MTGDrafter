import random
from typing import List, Dict

from .draft import Card, DraftPack, Player
from src.features.cardEncoders import CardEncoder # Import corretto con "src."

# --- 1. DEFINIRE PRIMA LA CLASSE BASE ---
class BaseBot:
    """
    Classe base per tutti i bot. Ogni bot deve avere un metodo 'pick'.
    """
    def __init__(self, player: Player):
        self.player = player

    def pick(self, pack: DraftPack, pack_number: int, pick_number: int) -> Card:
        """
        Sceglie una carta dalla busta.
        Questo metodo DEVE essere implementato dalle classi figlie.
        """
        raise NotImplementedError("Il metodo 'pick' deve essere implementato.")

# --- 2. POI DEFINIRE LE CLASSI CHE LA USANO ---
class RandomBot(BaseBot):
    """
    Un bot molto semplice che sceglie una carta a caso dalla busta.
    """
    def pick(self, pack: DraftPack, pack_number: int, pick_number: int) -> Card:
        """
        Sceglie una carta casuale dalla lista di carte nella busta.
        """
        print(f"Bot {self.player.player_id} (Random) sta scegliendo da una busta di {len(pack.cards)} carte.")
        chosen_card = random.choice(pack.cards)
        print(f"  -> Bot {self.player.player_id} ha scelto: {chosen_card.name}")
        return chosen_card

class ScoringBot(BaseBot):
    """
    Un bot che assegna un punteggio a ogni carta nella busta e sceglie la migliore.
    """
    def __init__(self, player: Player):
        super().__init__(player)
        self.encoder = CardEncoder()

    def _get_pool_colors(self) -> List[int]:
        pool_colors = [0, 0, 0, 0, 0]
        if not self.player.pool:
            return pool_colors

        for card in self.player.pool:
            card_colors = self.encoder._encode_colors(card.details)
            for i in range(5):
                pool_colors[i] += card_colors[i]
        
        return pool_colors

    def pick(self, pack: DraftPack, pack_number: int, pick_number: int) -> Card:
        pool_colors = self._get_pool_colors()
        best_card = None
        best_score = -1

        print(f"Bot {self.player.player_id} (Scoring) sta analizzando {len(pack.cards)} carte.")
        
        for card in pack.cards:
            card_features = self.encoder.encode_card(card.details)
            card_colors = card_features[0:5]
            color_synergy_score = sum(pool_colors[i] for i in range(5) if card_colors[i] > 0)
            cmc = card_features[5]
            quality_score = max(0, 8 - cmc)
            current_score = color_synergy_score + quality_score

            if current_score > best_score:
                best_score = current_score
                best_card = card

        if best_card is None:
            best_card = random.choice(pack.cards)

        print(f"  -> Bot {self.player.player_id} ha scelto: {best_card.name} (Punteggio: {best_score})")
        
        return best_card
