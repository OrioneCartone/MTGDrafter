import random
from typing import List, Dict
import torch
from pathlib import Path

# Import corretti
from src.environment.draft import Card, DraftPack, Player
from src.features.cardencoders import CardEncoder
from src.models.transformerdrafter import TransformerDrafter
from src.utils.constants import *

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
    """
    Versione "Maestro" auto-contenuta. Valuta le carte in modo olistico.
    """
    def __init__(self, player: Player):
        super().__init__(player)
        self.encoder = CardEncoder()

        self.weights = {
            "color_synergy": 1.5, "cmc_quality": 0.5, "evasion": 1.4, "combat": 1.2,
            "utility": 0.8, "mana_advantage": 1.3, "recursion": 1.2,
            "card_advantage": 1.8, "removal": 2.0, "synergy_engine": 1.6
        }
        
        self.keyword_indices = {name: i for i, name in enumerate(KEYWORD_LIST)}
        self.ability_indices = {name: i for i, name in enumerate(ABILITY_PATTERNS.keys())}
        
        self.keyword_offset = OLD_FEATURE_SIZE
        self.ability_offset = OLD_FEATURE_SIZE + len(KEYWORD_LIST)

    def _get_pool_colors(self) -> List[int]:
        pool_colors = [0] * 5
        for card in self.player.pool:
            card_colors = self.encoder._encode_colors(card.details)
            for i in range(5):
                pool_colors[i] += card_colors[i]
        return pool_colors

    def _get_feature(self, vec: List[float], f_type: str, f_name: str) -> int:
        """Helper robusto per ottenere il valore di una feature dal vettore."""
        try:
            if f_type == 'keyword':
                idx = self.keyword_offset + self.keyword_indices[f_name.lower()]
            elif f_type == 'ability':
                idx = self.ability_offset + self.ability_indices[f_name]
            else: return 0
            # Aggiunto controllo sui limiti per sicurezza
            if 0 <= idx < len(vec):
                return int(vec[idx])
            return 0
        except KeyError:
            return 0

    def pick(self, pack: DraftPack, pack_number: int, pick_number: int) -> Card:
        pool_colors = self._get_pool_colors()
        best_card, best_score = None, -1.0

        for card in pack.cards:
            features = self.encoder.encode_card(card.details)

            # Calcolo Punteggi Parziali (tutta la logica è interna alla classe)
            color_synergy = sum(pool_colors[i] for i in range(5) if features[i] > 0)
            cmc_quality = max(0, 5 - features[5])

            evasion = self._get_feature(features, 'keyword', 'Flying') * 3.0
            combat = self._get_feature(features, 'keyword', 'Deathtouch') * 2.0
            utility = self._get_feature(features, 'keyword', 'Lifelink') * 1.5
            mana_advantage = self._get_feature(features, 'ability', 'mana_dork') * 2.5
            recursion = self._get_feature(features, 'keyword', 'Flashback') * 2.5
            card_advantage = self._get_feature(features, 'ability', 'draw_multiple_cards') * 6.0
            removal = self._get_feature(features, 'ability', 'destroy_creature') * 5.0
            synergy_engine = self._get_feature(features, 'ability', 'spells_matter_payoff') * 3.0

            # Calcolo del Punteggio Finale Pesato
            final_score = (
                color_synergy * self.weights.get('color_synergy', 1.0) +
                cmc_quality * self.weights.get('cmc_quality', 1.0) +
                evasion * self.weights.get('evasion', 1.0) +
                combat * self.weights.get('combat', 1.0) +
                utility * self.weights.get('utility', 1.0) +
                mana_advantage * self.weights.get('mana_advantage', 1.0) +
                recursion * self.weights.get('recursion', 1.0) +
                card_advantage * self.weights.get('card_advantage', 1.0) +
                removal * self.weights.get('removal', 1.0) +
                synergy_engine * self.weights.get('synergy_engine', 1.0)
            )

            if final_score > best_score:
                best_score, best_card = final_score, card

        if best_card is None: best_card = random.choice(pack.cards)
        
        # print(f"  -> Bot {self.player.player_id} (Scoring) sceglie: {best_card.name} (Punteggio: {best_score:.2f})")
        return 
