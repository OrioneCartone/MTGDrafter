import json
import random
from pathlib import Path
from typing import List, Dict, Optional

from .draft import Card, DraftPack, Player
from .opponents import ScoringBot

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..training.logger import DraftLogger

class DraftSimulator:
    """
    Gestisce una simulazione completa di un draft di Magic.
    Può opzionalmente loggare ogni pick per la generazione di dati.
    """
    # Tutti i metodi seguenti devono avere questo livello di indentazione (4 spazi)
    def __init__(self, cube_list: List[Dict], bots: List[ScoringBot], 
                 num_players: int = 8, pack_size: int = 15, num_packs: int = 3,
                 draft_id: int = 0, logger: Optional['DraftLogger'] = None):
        
        if len(bots) != num_players:
            raise ValueError(f"Il numero di bot ({len(bots)}) non corrisponde al numero di giocatori ({num_players}).")
        
        self.num_players = num_players
        self.pack_size = pack_size
        self.num_packs = num_packs
        self.draft_id = draft_id
        self.logger = logger
        
        self.full_cube = self._load_cube(cube_list)
        random.shuffle(self.full_cube)
        self.players = [bot.player for bot in bots]
        self.bots = bots

    def _load_cube(self, cube_list: List[Dict]) -> List[Card]:
        """Converte la lista di dizionari JSON in una lista di oggetti Card."""
        return [Card(name=card_data.get('name', 'Sconosciuto'), details=card_data) for card_data in cube_list]
    
    def _create_packs(self) -> List[DraftPack]:
        """Crea le buste per un round di draft."""
        packs = []
        cards_needed = self.num_players * self.pack_size
        if len(self.full_cube) < cards_needed:
            raise ValueError(f"Carte insufficienti nel cubo ({len(self.full_cube)}) per un altro round ({cards_needed} necessarie).")
        
        for i in range(self.num_players):
            pack_cards_data = self.full_cube[:self.pack_size]
            self.full_cube = self.full_cube[self.pack_size:]
            pack = DraftPack(cards=pack_cards_data)
            packs.append(pack)
        return packs


    def run_draft(self, verbose: bool = False) -> Dict[int, Player]:
        """Esegue l'intera simulazione del draft."""
        if verbose: print(f"\n--- INIZIO DRAFT #{self.draft_id} ---")
        
        for pack_number in range(1, self.num_packs + 1):
            if verbose: print(f"\n--- Inizio Round {pack_number}/{self.num_packs} ---")
            current_packs = self._create_packs()

            for pick_number in range(1, self.pack_size + 1):
                if verbose: print(f"\n-- Pick {pick_number}/{self.pack_size} --")
                
                choices_this_turn = [None] * self.num_players
                
                # Fase 1: Ogni bot decide la sua mossa
                for i in range(self.num_players):
                    bot = self.bots[i]
                    pack_for_bot = current_packs[i]
                    chosen_card = bot.pick(pack_for_bot, pack_number, pick_number)
                    choices_this_turn[i] = chosen_card

                # Fase 2: Aggiorna lo stato e logga la decisione
                for i in range(self.num_players):
                    player = self.players[i]
                    chosen_card = choices_this_turn[i]
                    pack_before_pick = current_packs[i]
                    pool_before_pick = list(player.pool) # Copia del pool PRIMA di aggiungere la nuova carta

                    # --- LOGICA DI LOGGING CORRETTA ---
                    # Chiamiamo il logger qui, ora che abbiamo una 'chosen_card' valida.
                    if self.logger:
                        self.logger.log_pick(
                            draft_id=self.draft_id,
                            player_id=player.player_id,
                            pack_num=pack_number,
                            pick_num=pick_number,
                            pack=pack_before_pick.cards,
                            pool=pool_before_pick,
                            choice=chosen_card # Ora 'choice' non è mai None
                        )
                    # --- FINE LOGICA CORRETTA ---

                    # Finalizza l'azione
                    if chosen_card in pack_before_pick.cards:
                        player.add_to_pool(chosen_card)
                        pack_before_pick.cards.remove(chosen_card)
                
                # Fase 3: Passa le buste
                if pack_number % 2 == 1:
                    current_packs = current_packs[1:] + current_packs[:1]
                else:
                    current_packs = current_packs[-1:] + current_packs[:-1]

        if verbose: print(f"\n--- DRAFT #{self.draft_id} CONCLUSO ---")
        return {player.player_id: player for player in self.players}
