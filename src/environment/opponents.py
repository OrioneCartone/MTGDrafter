import random
from typing import List, Dict

from .draft import Card, DraftPack, Player
from src.features.cardEncoders import CardEncoder # Import corretto con "src."
from ..utils.constants import FEATURE_SIZE, MAX_PACK_SIZE, MAX_POOL_SIZE


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

# Aggiungi questi import all'inizio del file
import torch
from pathlib import Path
from ..models.policy_network import PolicyNetwork

# ... (il codice esistente di BaseBot, RandomBot, ScoringBot rimane qui) ...
# ...
# ...

# --- IL NOSTRO BOT BASATO SU RETE NEURALE ---
class AIBot(BaseBot):
    # Modifica il costruttore per non avere più feature_size come argomento fisso
    def __init__(self, player: Player, model_path: Path):
        super().__init__(player)
        self.encoder = CardEncoder()
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        print(f"Bot {self.player.player_id} (AI) sta caricando il modello da: {model_path}")
        if not model_path.exists():
            raise FileNotFoundError(f"File del modello non trovato: {model_path}")
            
        # Usa la costante importata
        self.model = PolicyNetwork(feature_size=FEATURE_SIZE)
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()
        print(f"Modello caricato con successo sul dispositivo '{self.device}'.")

    def pick(self, pack: DraftPack, pack_number: int, pick_number: int) -> Card:
        with torch.no_grad():
            pack_vectors = [self.encoder.encode_card(c.details) for c in pack.cards]
            pool_vectors = [self.encoder.encode_card(c.details) for c in self.player.pool]
            
            # --- CORREZIONE CHIAVE: USA LE COSTANTI ---
            pack_tensor = torch.zeros(1, MAX_PACK_SIZE, FEATURE_SIZE)
            pool_tensor = torch.zeros(1, MAX_POOL_SIZE, FEATURE_SIZE)
            # --- FINE CORREZIONE ---
            
            if pack_vectors:
                pack_tensor[0, :len(pack_vectors), :] = torch.tensor(pack_vectors, dtype=torch.float32)
            if pool_vectors:
                pool_tensor[0, :len(pool_vectors), :] = torch.tensor(pool_vectors, dtype=torch.float32)
                
            pack_tensor = pack_tensor.to(self.device)
            pool_tensor = pool_tensor.to(self.device)

            scores = self.model(pack_tensor, pool_tensor).squeeze(0)
            valid_scores = scores[:len(pack.cards)]
            best_card_index = torch.argmax(valid_scores).item()
            chosen_card = pack.cards[best_card_index]

            print(f"  -> Bot {self.player.player_id} (AI) ha scelto: {chosen_card.name} (Punteggio AI: {valid_scores[best_card_index]:.2f})")
            
            return chosen_card