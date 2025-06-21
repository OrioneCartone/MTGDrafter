import json
import random
from pathlib import Path
from typing import List, Dict

from .draft import Card, DraftPack, Player
from .opponents import BaseBot

# Definizione della classe
class DraftSimulator:
    # 1. Metodo __init__ (indentato di 4 spazi)
    def __init__(self, cube_list: List[Dict], bots: List[BaseBot], num_players: int = 8, pack_size: int = 15, num_packs: int = 3):
        if len(bots) != num_players:
            raise ValueError(f"Il numero di bot ({len(bots)}) non corrisponde al numero di giocatori ({num_players}).")
        self.num_players = num_players
        self.pack_size = pack_size
        self.num_packs = num_packs
        print("Caricamento del cubo...")
        self.full_cube = self._load_cube(cube_list)
        random.shuffle(self.full_cube)
        print(f"Cubo caricato e mischiato: {len(self.full_cube)} carte.")
        self.players = [bot.player for bot in bots]
        self.bots = bots

    # 2. Metodo _load_cube (indentato di 4 spazi, come __init__)
    def _load_cube(self, cube_list: List[Dict]) -> List[Card]:
        """Converte la lista di dizionari JSON in una lista di oggetti Card."""
        return [Card(name=card_data.get('name', 'Nome Sconosciuto'), details=card_data) for card_data in cube_list]

    # 3. Metodo _create_packs (indentato di 4 spazi)
    def _create_packs(self) -> List[DraftPack]:
        """Crea le buste per un round di draft."""
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

    # 4. Metodo run_draft (indentato di 4 spazi)
    def run_draft(self) -> Dict[int, Player]:
        """Esegue l'intera simulazione del draft."""
        print("\n--- INIZIO DRAFT ---")
        for pack_number in range(1, self.num_packs + 1):
            print(f"\n--- Inizio Round {pack_number}/{self.num_packs} ---")
            current_packs = self._create_packs()
            for pick_number in range(1, self.pack_size + 1):
                print(f"\n-- Pick {pick_number}/{self.pack_size} --")
                cards_picked_this_turn = []
                for i in range(self.num_players):
                    bot = self.bots[i]
                    player = self.players[i]
                    pack_for_bot = current_packs[i]
                    chosen_card = bot.pick(pack_for_bot, pack_number, pick_number)
                    player.add_to_pool(chosen_card)
                    cards_picked_this_turn.append((i, chosen_card))
                for i, card in cards_picked_this_turn:
                    current_packs[i].cards.remove(card)
                if pack_number % 2 == 1:
                    print("-> Passaggio buste a sinistra.")
                    current_packs = [current_packs[-1]] + current_packs[:-1]
                else:
                    print("<- Passaggio buste a destra.")
                    current_packs = current_packs[1:] + [current_packs[0]]
        print("\n--- DRAFT CONCLUSO ---")
        return {player.player_id: player for player in self.players}

