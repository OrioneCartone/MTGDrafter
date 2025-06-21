# src/environment/opponents.py
import random
from typing import List, Dict
import torch
from pathlib import Path

from src.environment.draft import Card, DraftPack, Player
from src.features.cardencoders import CardEncoder
from src.models.policynetwork import PolicyNetwork
from src.utils.constants import FEATURE_SIZE, MAX_PACK_SIZE, MAX_POOL_SIZE

# 1. CLASSE BASE
class BaseBot:
    def __init__(self, player: Player):
        self.player = player
    def pick(self, pack: DraftPack, pack_number: int, pick_number: int) -> Card:
        raise NotImplementedError("Il metodo 'pick' deve essere implementato da una sottoclasse.")

# 2. SOTTOCLASSI
class RandomBot(BaseBot):
    def pick(self, pack: DraftPack, pack_number: int, pick_number: int) -> Card:
        chosen_card = random.choice(pack.cards)
        print(f"  -> Bot {self.player.player_id} (Random) sceglie: {chosen_card.name}")
        return chosen_card

class ScoringBot(BaseBot):
    def __init__(self, player: Player):
        super().__init__(player)
        self.encoder = CardEncoder()

    def _get_pool_colors(self) -> List[int]:
        pool_colors = [0] * 5
        for card in self.player.pool:
            card_colors = self.encoder._encode_colors(card.details)
            for i in range(5):
                pool_colors[i] += card_colors[i]
        return pool_colors

    def pick(self, pack: DraftPack, pack_number: int, pick_number: int) -> Card:
        pool_colors = self._get_pool_colors()
        best_card, best_score = None, -1
        
        for card in pack.cards:
            features = self.encoder.encode_card(card.details)
            color_syn = sum(pool_colors[i] for i in range(5) if features[i] > 0)
            quality = max(0, 8 - features[5])
            score = color_syn + quality
            if score > best_score:
                best_score, best_card = score, card
        
        if best_card is None: best_card = random.choice(pack.cards)
        print(f"  -> Bot {self.player.player_id} (Scoring) sceglie: {best_card.name} (Punteggio: {best_score})")
        return best_card

class AIBot(BaseBot):
    def __init__(self, player: Player, model_path: Path):
        super().__init__(player)
        self.encoder = CardEncoder()
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        if not model_path.exists(): raise FileNotFoundError(f"File modello non trovato: {model_path}")
        
        self.model = PolicyNetwork(feature_size=FEATURE_SIZE)
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()
        print(f"Modello AI per Giocatore {player.player_id} caricato.")

    def pick(self, pack: DraftPack, pack_number: int, pick_number: int) -> Card:
        with torch.no_grad():
            pack_v = [self.encoder.encode_card(c.details) for c in pack.cards]
            pool_v = [self.encoder.encode_card(c.details) for c in self.player.pool]
            
            pack_t = torch.zeros(1, MAX_PACK_SIZE, FEATURE_SIZE, device=self.device)
            pool_t = torch.zeros(1, MAX_POOL_SIZE, FEATURE_SIZE, device=self.device)
            
            if pack_v: pack_t[0, :len(pack_v), :] = torch.tensor(pack_v, dtype=torch.float32)
            if pool_v: pool_t[0, :len(pool_v), :] = torch.tensor(pool_v, dtype=torch.float32)

            scores = self.model(pack_t, pool_t).squeeze(0)
            valid_scores = scores[:len(pack.cards)]
            best_idx = torch.argmax(valid_scores).item()
            chosen_card = pack.cards[best_idx]

            print(f"  -> Bot {self.player.player_id} (AI) sceglie: {chosen_card.name} (Punteggio AI: {valid_scores[best_idx]:.2f})")
            return chosen_card
