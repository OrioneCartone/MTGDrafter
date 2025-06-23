import random
from typing import List, Dict
import torch
from pathlib import Path
from collections import Counter # MODIFICA: Aggiunto l'import necessario per Counter

# Importiamo i moduli interni
from src.environment.draft import Card, DraftPack, Player
from src.features.cardencoders import CardEncoder
from src.models.transformerdrafter import TransformerDrafter 
from src.utils.config_loader import CONFIG

# Importa le costanti necessarie
from src.utils.constants import (
    FEATURE_SIZE, KEYWORD_LIST, ABILITY_PATTERNS, BASE_FEATURE_SIZE
)

# 1. CLASSE BASE
class BaseBot:
    def __init__(self, player: Player):
        self.player = player
    def pick(self, pack: DraftPack, pack_number: int, pick_number: int) -> Card:
        raise NotImplementedError("Il metodo 'pick' deve essere implementato da una sottoclasse.")

# 2. SOTTOCLASSI
class RandomBot(BaseBot):
    """Un bot che sceglie una carta completamente a caso."""
    def pick(self, pack: DraftPack, pack_number: int, pick_number: int) -> Card:
        chosen_card = random.choice(pack.cards)
        # print(f"  -> Bot {self.player.player_id} (Random) sceglie: {chosen_card.name}")
        return chosen_card


class ScoringBot(BaseBot):
    """
    Versione "Maestro" evoluta. Valuta le carte considerando il segnale,
    la curva di mana e le sinergie del mazzo in costruzione.
    """
    def __init__(self, player: Player):
        super().__init__(player)
        self.encoder = CardEncoder()

        # Dizionari per accedere agli indici delle feature
        self.keyword_indices = {name.lower(): i for i, name in enumerate(KEYWORD_LIST)}
        self.ability_indices = {name: i for i, name in enumerate(ABILITY_PATTERNS.keys())}
        self.keyword_offset = BASE_FEATURE_SIZE
        self.ability_offset = BASE_FEATURE_SIZE + len(KEYWORD_LIST)

        # Pesi per la valutazione
        self.base_weights = {
            "removal": 2.5, "card_advantage": 2.2, "evasion": 1.5, "mana_advantage": 1.8,
            "board_wipe": 3.0, "synergy_engine": 1.6, "combat_trick": 1.2, "recursion": 1.2
        }
        self.context_weights = {
            "color_commitment": 3.0, "splash_penalty": -5.0,
            "curve_bonus": 1.5, "signal_bonus": 4.0
        }
        
        # Stato interno del bot, correttamente inizializzato
        self.main_colors = set()
        self.color_commitment = Counter()
        self.mana_curve = Counter()

    def _get_feature(self, vec: List[float], f_type: str, f_name: str) -> int:
        """Helper robusto per ottenere il valore di una feature dal vettore."""
        try:
            if f_type == 'keyword':
                idx = self.keyword_offset + self.keyword_indices[f_name.lower()]
            elif f_type == 'ability':
                idx = self.ability_offset + self.ability_indices[f_name]
            else: return 0
            if 0 <= idx < len(vec): return int(vec[idx])
            return 0
        except KeyError:
            return 0

    def _update_state(self):
        """Aggiorna la percezione del bot sui suoi colori e la sua curva."""
        self.mana_curve.clear()
        self.color_commitment.clear()
        
        for card in self.player.pool:
            cmc = card.details.get('cmc', 0)
            if cmc > 0: self.mana_curve[int(cmc)] += 1
            
            colors = card.details.get('colors', [])
            if colors:
                for color in colors: self.color_commitment[color] += 1
        
        if len(self.player.pool) > 5:
            top_colors = self.color_commitment.most_common(2)
            self.main_colors = {color for color, count in top_colors}

    def _calculate_base_score(self, features: List[float]) -> float:
        """Calcola il punteggio 'grezzo' di una carta, basato sulle sue abilità intrinseche."""
        score = 0.0
        score += self._get_feature(features, 'ability', 'destroy_creature') * self.base_weights['removal']
        score += self._get_feature(features, 'ability', 'draw_multiple_cards') * self.base_weights['card_advantage']
        score += self._get_feature(features, 'keyword', 'flying') * self.base_weights['evasion']
        score += self._get_feature(features, 'ability', 'mana_dork') * self.base_weights['mana_advantage']
        score += self._get_feature(features, 'ability', 'board_wipe_damage') * self.base_weights['board_wipe']
        score += self._get_feature(features, 'ability', 'spells_matter_payoff') * self.base_weights['synergy_engine']
        score += self._get_feature(features, 'ability', 'pump_single_trick') * self.base_weights['combat_trick']
        score += self._get_feature(features, 'ability', 'graveyard_recursion_creature') * self.base_weights['recursion']
        return score

    def _calculate_contextual_bonuses(self, card: Card, features: List[float], pick_number: int) -> float:
        """Calcola i bonus basati sullo stato attuale del draft."""
        context_score = 0.0
        card_colors = set(card.details.get('colors', []))
        
        # 1. Bonus Colore
        if self.main_colors:
            if card_colors.issubset(self.main_colors):
                context_score += self.context_weights['color_commitment']
            elif not card_colors.intersection(self.main_colors) and len(self.main_colors) >= 2:
                context_score += self.context_weights['splash_penalty']

        # 2. Bonus Curva
        cmc = int(card.details.get('cmc', 0))
        if 1 < cmc < 7 and self.mana_curve: # Aggiunto controllo per evitare errori su curve vuote
            most_common_count = self.mana_curve.most_common(1)[0][1]
            if self.mana_curve[cmc] < most_common_count:
                 context_score += self.context_weights['curve_bonus'] / (self.mana_curve[cmc] + 1)

        # 3. Bonus Segnale
        if pick_number > 3:
            base_power = self._calculate_base_score(features)
            if base_power > self.base_weights['removal']: # Se una carta forte arriva tardi
                context_score += self.context_weights['signal_bonus'] * (pick_number / 15.0)

        return context_score

    def pick(self, pack: DraftPack, pack_number: int, pick_number: int) -> Card:
        self._update_state()
        best_card, best_score = None, -999.0

        for card in pack.cards:
            features = self.encoder.encode_card(card.details)
            base_score = self._calculate_base_score(features)
            context_bonus = self._calculate_contextual_bonuses(card, features, pick_number)
            final_score = base_score + context_bonus

            if final_score > best_score:
                best_score, best_card = final_score, card

        if best_card is None: best_card = random.choice(pack.cards)
        return best_card


class AIBot(BaseBot):
    """
    Un bot che usa il modello TransformerDrafter addestrato per prendere decisioni.
    """
    def __init__(self, player: Player, model_path: Path):
        super().__init__(player)
        self.encoder = CardEncoder()
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        if not model_path.exists():
            raise FileNotFoundError(f"File modello non trovato: {model_path}")
            
        model_config = CONFIG['model']
        self.model = TransformerDrafter(
            feature_size=FEATURE_SIZE,
            embed_dim=model_config['embed_dim'],
            hidden_dim=model_config['hidden_dim'],
            n_heads=model_config['n_heads'],
            n_layers=model_config['n_layers'],
            dropout=model_config['dropout']
        )
        
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()

    def pick(self, pack: DraftPack, pack_number: int, pick_number: int) -> Card:
        with torch.no_grad():
            pack_vectors = [self.encoder.encode_card(c.details) for c in pack.cards]
            pool_vectors = [self.encoder.encode_card(c.details) for c in self.player.pool]
            
            max_pack = CONFIG['model']['max_pack_size']
            max_pool = CONFIG['model']['max_pool_size']

            pack_tensor = torch.zeros(1, max_pack, FEATURE_SIZE, device=self.device)
            pool_tensor = torch.zeros(1, max_pool, FEATURE_SIZE, device=self.device)
            
            if pack_vectors: pack_tensor[0, :len(pack_vectors), :] = torch.tensor(pack_vectors, dtype=torch.float32)
            if pool_vectors: pool_tensor[0, :len(pool_vectors), :] = torch.tensor(pool_vectors, dtype=torch.float32)

            absolute_pick_number = (pack_number - 1) * 15 + pick_number
            pick_tensor = torch.tensor([absolute_pick_number], dtype=torch.long, device=self.device)

            scores = self.model(pack_tensor, pool_tensor, pick_tensor).squeeze(0)
            
            valid_scores = scores[:len(pack.cards)]
            best_card_index = torch.argmax(valid_scores).item()
            
            return pack.cards[best_card_index]