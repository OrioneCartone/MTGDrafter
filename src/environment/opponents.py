import random
from typing import List, Dict
import torch
from pathlib import Path

# Importiamo i moduli interni
from src.environment.draft import Card, DraftPack, Player
from src.features.cardencoders import CardEncoder
from src.models.policynetwork import PolicyNetwork

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
    Una versione avanzata dello ScoringBot che valuta le carte in modo olistico,
    considerando colori, curva, qualità, keyword e abilità testuali.
    Questo bot funge da "maestro" per la generazione di log di training di alta qualità.
    """
    def __init__(self, player: Player):
        super().__init__(player)
        self.encoder = CardEncoder()

        # Definiamo i pesi per ogni componente del punteggio.
        # Questo ci permette di bilanciare facilmente l'importanza di ogni aspetto.
        self.weights = {
            "color_synergy": 1.5, "cmc_quality": 0.5, "evasion": 1.2,
            "combat_tricks": 1.0, "removal": 1.8, "card_advantage": 1.5,
            "ramp_fixing": 1.2, "synergy_engine": 1.3
        }
        self.keyword_indices = {name: i for i, name in enumerate(KEYWORD_LIST)}
        self.ability_indices = {name: i for i, name in enumerate(ABILITY_PATTERNS.keys())}
        self.keyword_offset = OLD_FEATURE_SIZE
        self.ability_offset = OLD_FEATURE_SIZE + len(KEYWORD_LIST)


    def _get_pool_colors(self) -> List[int]:
        # ... (questo metodo rimane invariato) ...
        pool_colors = [0] * 5
        for card in self.player.pool:
            card_colors = self.encoder._encode_colors(card.details)
            for i in range(5):
                pool_colors[i] += card_colors[i]
        return pool_colors

    def _get_feature_value(self, vec: List[float], feature_type: str, feature_name: str) -> int:
        """Helper per ottenere il valore di una feature dal vettore usando i nomi."""
        if feature_type == 'keyword':
            idx = self.keyword_offset + self.keyword_indices.get(feature_name, -1)
        elif feature_type == 'ability':
            idx = self.ability_offset + self.ability_indices.get(feature_name, -1)
        else:
            return 0
        
        if 0 <= idx < len(vec):
            return int(vec[idx])
        return 0

    def pick(self, pack: DraftPack, pack_number: int, pick_number: int) -> Card:
        pool_colors = self._get_pool_colors()
        best_card, best_score = None, -1

        for card in pack.cards:
            features = self.encoder.encode_card(card.details)

            # --- Calcolo dei Punteggi Parziali ---

            # 1. Sinergia di Colore
            color_synergy = sum(pool_colors[i] for i in range(5) if features[i] > 0)
            
            # 2. Qualità basata sul CMC (penalizza carte costose)
            cmc = features[5]
            cmc_quality = max(0, 5 - cmc) # Un po' meno aggressivo di prima

            # 3. Punteggio Evasione (Volare, Menace, etc.)
            evasion = (self._get_feature_value(features, 'keyword', 'Flying') * 3.0 +
                       self._get_feature_value(features, 'keyword', 'Menace') * 1.5 +
                       self._get_feature_value(features, 'keyword', 'Skulk') * 1.0)

            # 4. Punteggio Abilità di Combattimento
            combat_tricks = (self._get_feature_value(features, 'keyword', 'Deathtouch') * 2.0 +
                             self._get_feature_value(features, 'keyword', 'First strike') * 1.5 +
                             self._get_feature_value(features, 'keyword', 'Double strike') * 3.0 +
                             self._get_feature_value(features, 'keyword', 'Lifelink') * 1.5)

            # 5. Punteggio Rimozioni
            removal = (self._get_feature_value(features, 'ability', 'destroy_creature') * 5.0 +
                       self._get_feature_value(features, 'ability', 'exile_permanent') * 6.0 +
                       self._get_feature_value(features, 'ability', 'damage_to_creature') * 3.0 +
                       self._get_feature_value(features, 'ability', 'counter_spell') * 4.0 +
                       self._get_feature_value(features, 'ability', 'pacifism') * 3.0)

            # 6. Punteggio Vantaggio Carte
            card_advantage = (self._get_feature_value(features, 'ability', 'draw_multiple_cards') * 6.0 +
                              self._get_feature_value(features, 'ability', 'cantrip') * 4.0 +
                              self._get_feature_value(features, 'ability', 'draw_card') * 2.5)

            # 7. Punteggio Rampa e Fixing di Mana
            ramp_fixing = (self._get_feature_value(features, 'ability', 'mana_ramp') * 2.0 +
                           self._get_feature_value(features, 'ability', 'mana_fix') * 1.5)
            
            # 8. Punteggio Motori di Sinergia
            synergy_engine = (self._get_feature_value(features, 'ability', 'pump_all') * 4.0 +
                              self._get_feature_value(features, 'ability', 'sac_outlet') * 2.0 +
                              self._get_feature_value(features, 'ability', 'graveyard_recursion') * 3.0)

            # --- Calcolo del Punteggio Finale Pesato ---
            final_score = (
                color_synergy * self.weights['color_synergy'] +
                cmc_quality * self.weights['cmc_quality'] +
                evasion * self.weights['evasion'] +
                combat_tricks * self.weights['combat_tricks'] +
                removal * self.weights['removal'] +
                card_advantage * self.weights['card_advantage'] +
                ramp_fixing * self.weights['ramp_fixing'] +
                synergy_engine * self.weights['synergy_engine']
            )

            if final_score > best_score:
                best_score, best_card = final_score, card

        if best_card is None:
            best_card = random.choice(pack.cards)
        
        # Riduciamo la verbosità durante la generazione dei log
        # print(f"  -> Bot {self.player.player_id} (Scoring v2) sceglie: {best_card.name} (Punteggio: {best_score:.2f})")
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
