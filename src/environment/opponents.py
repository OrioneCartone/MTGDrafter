import random
from typing import List, Dict
import torch
from pathlib import Path

# Importiamo i moduli interni
from src.environment.draft import Card, DraftPack, Player
from src.features.cardencoders import CardEncoder
from src.models.policynetwork import PolicyNetwork
from src.models.transformerdrafter import TransformerDrafter # Importa il nuovo modello

# --- MODIFICA CHIAVE: Importa TUTTE le costanti necessarie ---
from src.utils.constants import (
    FEATURE_SIZE, MAX_PACK_SIZE, MAX_POOL_SIZE, 
    KEYWORD_LIST, ABILITY_PATTERNS, OLD_FEATURE_SIZE
)

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
    Una versione "Maestro" dello ScoringBot. Valuta le carte in modo olistico,
    utilizzando un sistema di punteggio pesato per tutte le feature definite
    in constants.py. Funge da generatore di dati di alta qualità.
    """
    def __init__(self, player: Player):
        super().__init__(player)
        self.encoder = CardEncoder()

        # Definiamo i pesi per ogni categoria di valutazione.
        self.weights = {
            "color_synergy": 1.5,
            "cmc_quality": 0.5,
            "evasion": 1.4,
            "combat": 1.2,
            "utility": 0.8,
            "mana_advantage": 1.3,
            "recursion": 1.2,
            "card_advantage": 1.8,
            "removal": 2.0,  # Le rimozioni sono estremamente importanti
            "synergy_engine": 1.6
        }
        
        # Mappatura degli indici per una lettura leggibile del codice
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
                idx = self.keyword_offset + self.keyword_indices[f_name]
            elif f_type == 'ability':
                idx = self.ability_offset + self.ability_indices[f_name]
            else: return 0
            return int(vec[idx])
        except (KeyError, IndexError):
            return 0

    def pick(self, pack: DraftPack, pack_number: int, pick_number: int) -> Card:
        pool_colors = self._get_pool_colors()
        best_card, best_score = None, -1.0

        for card in pack.cards:
            features = self.encoder.encode_card(card.details)

            # --- Calcolo dei Punteggi Parziali per Categoria ---
            color_synergy = sum(pool_colors[i] for i in range(5) if features[i] > 0)
            cmc_quality = max(0, 5 - features[5])

            evasion = (self._get_feature(features, 'keyword', 'Flying') * 3.0 +
                       self._get_feature(features, 'keyword', 'Shadow') * 3.0 +
                       self._get_feature(features, 'keyword', 'Menace') * 1.5 +
                       self._get_feature(features, 'keyword', 'Skulk') * 1.0)
            
            combat = (self._get_feature(features, 'keyword', 'Deathtouch') * 2.0 +
                      self._get_feature(features, 'keyword', 'First strike') * 1.5 +
                      self._get_feature(features, 'keyword', 'Double strike') * 3.0 +
                      self._get_feature(features, 'keyword', 'Trample') * 1.0)

            utility = (self._get_feature(features, 'keyword', 'Lifelink') * 1.5 +
                       self._get_feature(features, 'keyword', 'Vigilance') * 1.0 +
                       self._get_feature(features, 'keyword', 'Haste') * 1.2 +
                       self._get_feature(features, 'keyword', 'Flash') * 1.2)

            mana_advantage = (self._get_feature(features, 'ability', 'mana_ramp_creature') * 2.5 +
                              self._get_feature(features, 'ability', 'mana_ramp_spell') * 1.5 +
                              self._get_feature(features, 'ability', 'mana_fix') * 1.0 +
                              self._get_feature(features, 'ability', 'cost_reduction') * 2.0)

            recursion = (self._get_feature(features, 'keyword', 'Unearth') * 2.0 +
                         self._get_feature(features, 'keyword', 'Flashback') * 2.5 +
                         self._get_feature(features, 'ability', 'graveyard_recursion_creature') * 3.0)

            card_advantage = (self._get_feature(features, 'ability', 'draw_multiple_cards') * 6.0 +
                              self._get_feature(features, 'ability', 'cantrip') * 4.0 +
                              self._get_feature(features, 'ability', 'draw_card') * 2.0 +
                              self._get_feature(features, 'ability', 'investigate') * 2.5 +
                              self._get_feature(features, 'ability', 'monarch') * 7.0 + # Monarch è fortissimo
                              self._get_feature(features, 'ability', 'initiative') * 6.0) # Anche initiative

            removal = (self._get_feature(features, 'ability', 'exile_permanent') * 6.0 +
                       self._get_feature(features, 'ability', 'destroy_creature') * 5.0 +
                       self._get_feature(features, 'ability', 'damage_to_any_target') * 4.0 +
                       self._get_feature(features, 'ability', 'counter_spell_hard') * 4.5 +
                       self._get_feature(features, 'ability', 'edict_effect') * 3.5 +
                       self._get_feature(features, 'ability', 'pacifism_effect') * 3.0)

            synergy_engine = (self._get_feature(features, 'ability', 'spells_matter_payoff') * 3.0 +
                              self._get_feature(features, 'ability', 'artifacts_matter_payoff') * 3.0 +
                              self._get_feature(features, 'ability', 'sac_outlet') * 2.5 +
                              self._get_feature(features, 'ability', 'payoff_for_sac') * 3.5 +
                              self._get_feature(features, 'ability', 'pump_all_static') * 5.0)

            # --- Calcolo del Punteggio Finale Pesato ---
            final_score = (
                color_synergy       * self.weights['color_synergy']     +
                cmc_quality         * self.weights['cmc_quality']       +
                evasion             * self.weights['evasion']           +
                combat              * self.weights['combat']            +
                utility             * self.weights['utility']           +
                mana_advantage      * self.weights['mana_advantage']    +
                recursion           * self.weights['recursion']         +
                card_advantage      * self.weights['card_advantage']    +
                removal             * self.weights['removal']           +
                synergy_engine      * self.weights['synergy_engine']
            )

            if final_score > best_score:
                best_score, best_card = final_score, card

        if best_card is None:
            best_card = random.choice(pack.cards)
        
        # print(f"  -> Bot {self.player.player_id} (Scoring v2) sceglie: {best_card.name} (Punteggio: {best_score:.2f})")
        return best_card



class AIBot(BaseBot):
    """
    Un bot che usa il modello TransformerDrafter addestrato per prendere decisioni.
    """
    # Rimuoviamo 'model_type' dal costruttore
    def __init__(self, player: Player, model_path: Path):
        super().__init__(player)
        self.encoder = CardEncoder()
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        print(f"Bot {player.player_id} (AI) sta caricando il modello Transformer da: {model_path}")
        if not model_path.exists():
            raise FileNotFoundError(f"File modello non trovato: {model_path}")
            
        # Carichiamo direttamente il TransformerDrafter, non c'è più ambiguità
        self.model = TransformerDrafter()
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()
        print(f"Modello Transformer per Giocatore {player.player_id} caricato con successo.")

    def pick(self, pack: DraftPack, pack_number: int, pick_number: int) -> Card:
        with torch.no_grad():
            pack_vectors = [self.encoder.encode_card(c.details) for c in pack.cards]
            pool_vectors = [self.encoder.encode_card(c.details) for c in self.player.pool]
            
            pack_tensor = torch.zeros(1, MAX_PACK_SIZE, FEATURE_SIZE, device=self.device)
            pool_tensor = torch.zeros(1, MAX_POOL_SIZE, FEATURE_SIZE, device=self.device)
            
            if pack_vectors: pack_tensor[0, :len(pack_vectors), :] = torch.tensor(pack_vectors, dtype=torch.float32)
            if pool_vectors: pool_tensor[0, :len(pool_vectors), :] = torch.tensor(pool_vectors, dtype=torch.float32)

            absolute_pick_number = (pack_number - 1) * 15 + pick_number
            pick_tensor = torch.tensor([absolute_pick_number], dtype=torch.long, device=self.device)

            scores = self.model(pack_tensor, pool_tensor, pick_tensor).squeeze(0)
            
            valid_scores = scores[:len(pack.cards)]
            best_card_index = torch.argmax(valid_scores).item()
            chosen_card = pack.cards[best_card_index]

            print(f"  -> Bot {self.player.player_id} (AI-T) sceglie: {chosen_card.name} (Punteggio: {valid_scores[best_card_index]:.2f})")
            return chosen_card