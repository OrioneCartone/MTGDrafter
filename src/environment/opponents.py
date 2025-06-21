import random
from typing import List
from .draft import Card, DraftPack, Player # Importiamo le nostre nuove classi

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

class RandomBot(BaseBot):
    """
    Un bot molto semplice che sceglie una carta a caso dalla busta.
    """
    def pick(self, pack: DraftPack, pack_number: int, pick_number: int) -> Card:
        """
        Sceglie una carta casuale dalla lista di carte nella busta.
        """
        print(f"Bot {self.player.player_id} (Random) sta scegliendo da una busta di {len(pack.cards)} carte.")
        
        # Scegli una carta a caso
        chosen_card = random.choice(pack.cards)
        
        # Aggiungi la carta scelta al suo pool
        self.player.add_to_pool(chosen_card)
        
        print(f"  -> Bot {self.player.player_id} ha scelto: {chosen_card.name}")
        
        return chosen_card
