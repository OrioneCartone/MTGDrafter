import json
import random
from pathlib import Path
from typing import List, Dict

# Importiamo le classi che abbiamo definito negli altri file
from .draft import Card, DraftPack, Player
from .opponents import BaseBot, RandomBot

class DraftSimulator:
    """
    Gestisce una simulazione completa di un draft di Magic.
    È un "arbitro stupido": conosce le regole del draft, ma non del gioco.
    """
    def __init__(self, cube_list: List[Dict], bots: List[BaseBot], num_players: int = 8, pack_size: int = 15, num_packs: int = 3):
        if len(bots) != num_players:
            raise ValueError(f"Il numero di bot ({len(bots)}) non corrisponde al numero di giocatori ({num_players}).")

        self.num_players = num_players
        self.pack_size = pack_size
        self.num_packs = num_packs
        
        # 1. Carica e mischia il cubo
        print("Caricamento del cubo...")
        self.full_cube = self._load_cube(cube_list)
        random.shuffle(self.full_cube)
        print(f"Cubo caricato e mischiato: {len(self.full_cube)} carte.")
        
        # 2. Associa i bot ai giocatori
        self.players = [bot.player for bot in bots]
        self.bots = bots

    def _load_cube(self, cube_list: List[Dict]) -> List[Card]:
        """Converte la lista di dizionari JSON in una lista di oggetti Card."""
        return [Card(name=card_data.get('name', 'Nome Sconosciuto'), details=card_data) for card_data in cube_list]

    def _create_packs(self) -> List[DraftPack]:
        """Crea le buste per un round di draft."""
        packs = []
        # Calcola quante carte servono per un round
        cards_needed = self.num_players * self.pack_size
        if len(self.full_cube) < cards_needed:
            raise ValueError("Non ci sono abbastanza carte nel cubo per creare le buste per tutti i giocatori.")
            
        print(f"Creo {self.num_players} buste da {self.pack_size} carte...")
        for i in range(self.num_players):
            # Prende le prime 'pack_size' carte dal cubo mischiato
            pack_cards_data = self.full_cube[:self.pack_size]
            # E le rimuove dal cubo, così non vengono riutilizzate
            self.full_cube = self.full_cube[self.pack_size:]
            
            pack = DraftPack(cards=pack_cards_data)
            packs.append(pack)
        
        return packs

    def run_draft(self) -> Dict[int, Player]:
        """
        Esegue l'intera simulazione del draft.
        """
        print("\n--- INIZIO DRAFT ---")
        
        for pack_number in range(1, self.num_packs + 1):
            print(f"\n--- Inizio Round {pack_number}/{self.num_packs} ---")
            
            # Crea le buste per il round corrente
            current_packs = self._create_packs()

            # Drafta tutte le carte nelle buste
            for pick_number in range(1, self.pack_size + 1):
                print(f"\n-- Pick {pick_number}/{self.pack_size} --")
                
                picks_this_turn = {} # Qui salviamo le scelte di questo turno
                
                # Ogni bot fa la sua scelta in parallelo (concettualmente)
                for i in range(self.num_players):
                    bot = self.bots[i]
                    pack_for_bot = current_packs[i]
                    
                    # Il bot sceglie una carta dalla busta
                    chosen_card = bot.pick(pack_for_bot, pack_number, pick_number)
                    
                    # Salviamo la carta scelta e la rimuoviamo dalla busta
                    picks_this_turn[i] = chosen_card
                    pack_for_bot.cards.remove(chosen_card)

                # Le buste vengono passate ai giocatori
                # La direzione del passaggio cambia ad ogni round
                if pack_number % 2 == 1: # Round 1 e 3: passa a sinistra
                    print("-> Passaggio buste a sinistra.")
                    # Il primo giocatore riceve la busta dall'ultimo, il secondo dal primo, ecc.
                    current_packs = [current_packs[-1]] + current_packs[:-1]
                else: # Round 2: passa a destra
                    print("<- Passaggio buste a destra.")
                    # Il primo giocatore riceve la busta dal secondo, ecc.
                    current_packs = current_packs[1:] + [current_packs[0]]

        print("\n--- DRAFT CONCLUSO ---")
        
        # Restituisce i giocatori con i loro mazzi completi
        return {player.player_id: player for player in self.players}

