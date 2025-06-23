import json
import random
from pathlib import Path
from typing import List, Dict, Optional

from .draft import Card, DraftPack, Player
from .opponents import BaseBot # MODIFICA: Importa la classe base per accettare tutti i tipi di bot

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..training.logger import DraftLogger

class DraftSimulator:
    """
    Gestisce una simulazione completa di un draft di Magic.
    Può opzionalmente loggare ogni pick per la generazione di dati.
    """
    # Tutti i metodi seguenti devono avere questo livello di indentazione (4 spazi)
    def __init__(self, cube_list: List[Dict], bots: List[BaseBot], # MODIFICA: Usa BaseBot per flessibilità
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

            # Determina la direzione di passaggio (es. orario per round 1 e 3, antiorario per 2)
            pass_direction = 1 if (pack_number % 2) != 0 else -1

            for pick_number in range(1, self.pack_size + 1):
                if verbose: print(f"\n-- Pick {pick_number}/{self.pack_size} --")
                
                choices_this_turn = {} # Usiamo un dizionario per mappare bot -> scelta
                
                # Fase 1: Ogni bot decide la sua mossa in parallelo (concettualmente)
                for i in range(self.num_players):
                    bot = self.bots[i]
                    pack_for_bot = current_packs[i]
                    if pack_for_bot and pack_for_bot.cards: # Assicurati che il pacchetto non sia vuoto
                        chosen_card = bot.pick(pack_for_bot, pack_number, pick_number)
                        choices_this_turn[i] = (chosen_card, pack_for_bot)

                # Fase 2: Aggiorna stato, logga e prepara i pacchetti per il passaggio
                next_packs = [None] * self.num_players
                for i in range(self.num_players):
                    if i not in choices_this_turn:
                        continue

                    chosen_card, pack_before_pick = choices_this_turn[i]
                    player = self.players[i]
                    pool_before_pick = list(player.pool)

                    if self.logger:
                        self.logger.log_pick(
                            draft_id=self.draft_id, player_id=player.player_id,
                            pack_num=pack_number, pick_num=pick_number,
                            pack=list(pack_before_pick.cards), # CORREZIONE: Passa una copia della lista per un logging sicuro
                            pool=pool_before_pick,
                            choice=chosen_card
                        )
                    
                    player.add_to_pool(chosen_card)
                    pack_before_pick.remove_card(chosen_card) # ORA FUNZIONA: Chiama il metodo che abbiamo aggiunto

                    # Prepara il pacchetto per il prossimo giocatore
                    pass_to_index = (i + pass_direction) % self.num_players
                    next_packs[pass_to_index] = pack_before_pick
                
                current_packs = next_packs # I pacchetti sono stati passati

        if verbose: print(f"\n--- FINE DRAFT #{self.draft_id} ---\n")
        return {p.player_id: p for p in self.players}