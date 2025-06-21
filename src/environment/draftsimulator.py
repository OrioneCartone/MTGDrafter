import json
import random
from pathlib import Path
from typing import List, Dict, Optional # Aggiungi Optional

from .draft import Card, DraftPack, Player
from .opponents import BaseBot
# Aggiungi un riferimento a DraftLogger, anche se verrà passato dall'esterno
# Questo si chiama "type hinting forward reference"
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..training.logger import DraftLogger


class DraftSimulator:
    """
    Gestisce una simulazione completa di un draft di Magic.
    Può opzionalmente loggare ogni pick per la generazione di dati.
    """
    # --- MODIFICA 1: Aggiungi il logger opzionale al costruttore ---
    def __init__(self, cube_list: List[Dict], bots: List[BaseBot], 
                 num_players: int = 8, pack_size: int = 15, num_packs: int = 3,
                 draft_id: int = 0, logger: Optional['DraftLogger'] = None):
        # ... (il codice di controllo e le assegnazioni base rimangono uguali) ...
        if len(bots) != num_players:
            raise ValueError(f"Il numero di bot ({len(bots)}) non corrisponde al numero di giocatori ({num_players}).")
        self.num_players = num_players
        self.pack_size = pack_size
        self.num_packs = num_packs
        
        # --- MODIFICA 2: Salva il logger e l'ID del draft ---
        self.draft_id = draft_id
        self.logger = logger
        
        print("Caricamento del cubo...")
        self.full_cube = self._load_cube(cube_list)
        random.shuffle(self.full_cube)
        print(f"Cubo caricato e mischiato: {len(self.full_cube)} carte.")
        self.players = [bot.player for bot in bots]
        self.bots = bots

    # ... (i metodi _load_cube e _create_packs rimangono invariati) ...
    def _load_cube(self, cube_list: List[Dict]) -> List[Card]:
        return [Card(name=card_data.get('name', 'Nome Sconosciuto'), details=card_data) for card_data in cube_list]
    
    def _create_packs(self) -> List[DraftPack]:
        # ... codice esistente ...
        packs = []
        cards_needed = self.num_players * self.pack_size
        if len(self.full_cube) < cards_needed:
            raise ValueError("Non ci sono abbastanza carte nel cubo per creare le buste per tutti i giocatori.")
        print(f"Creo {self.num_players} buste da {self.pack_size} carte...")
        for i in range(self.num_players):
            pack_cards_data = self.full_cube[:self.pack_size]
            self.full_cube = self.full_cube[self.pack_size:]
            pack = DraftPack(cards=pack_cards_data)
            packs.append(pack)
        return packs

    def run_draft(self) -> Dict[int, Player]:
        """Esegue l'intera simulazione del draft."""
        print(f"\n--- INIZIO DRAFT #{self.draft_id} ---")
        for pack_number in range(1, self.num_packs + 1):
            # ... (la logica di creazione delle buste rimane uguale) ...
            current_packs = self._create_packs()
            
            for pick_number in range(1, self.pack_size + 1):
                # ... (il print del pick rimane uguale) ...
                
                cards_picked_this_turn = []
                for i in range(self.num_players):
                    bot = self.bots[i]
                    player = self.players[i]
                    pack_for_bot = current_packs[i]
                    
                    # --- MODIFICA 3: Logga lo stato PRIMA della decisione ---
                    if self.logger:
                        # Clona il pool attuale per evitare di loggare la scelta prima che sia fatta
                        pool_before_pick = list(player.pool)

                    # Il bot sceglie una carta
                    chosen_card = bot.pick(pack_for_bot, pack_number, pick_number)
                    
                    # --- MODIFICA 4: Logga la decisione PRESA ---
                    if self.logger:
                        self.logger.log_pick(
                            draft_id=self.draft_id,
                            player_id=player.player_id,
                            pack_num=pack_number,
                            pick_num=pick_number,
                            pack=pack_for_bot.cards,
                            pool=pool_before_pick,
                            choice=chosen_card
                        )

                    # Aggiorna lo stato del gioco
                    player.add_to_pool(chosen_card)
                    cards_picked_this_turn.append((i, chosen_card))

                # ... (il resto del codice per rimuovere le carte e passare le buste rimane invariato) ...
                for i, card in cards_picked_this_turn:
                    current_packs[i].cards.remove(card)
                if pack_number % 2 == 1:
                    current_packs = [current_packs[-1]] + current_packs[:-1]
                else:
                    current_packs = current_packs[1:] + [current_packs[0]]

        print(f"\n--- DRAFT #{self.draft_id} CONCLUSO ---")
        return {player.player_id: player for player in self.players}

