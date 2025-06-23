import random
from typing import List, Dict, Optional, Any

from src.environment.draft import Card, DraftPack, Player
from src.training.logger import DraftLogger

class DraftSimulator:
    """
    Gestisce la logica di una singola simulazione di draft,
    distribuendo i pacchetti e coordinando le scelte dei bot.
    """
    def __init__(
        self,
        # MODIFICA: Accetta direttamente una lista di oggetti Card
        cube_list: List[Card], 
        bots: List,
        num_players: int,
        pack_size: int,
        num_packs: int,
        draft_id: Any,
        logger: Optional[DraftLogger] = None
    ):
        if len(bots) != num_players:
            raise ValueError("Il numero di bot deve corrispondere al numero di giocatori.")
        
        self.bots = bots
        self.players = [bot.player for bot in bots]
        self.num_players = num_players
        self.pack_size = pack_size
        self.num_packs = num_packs
        self.draft_id = draft_id
        self.logger = logger
        
        # MODIFICA: Assegna direttamente la lista di carte, senza conversioni
        self.full_cube = cube_list
        self.remaining_cards = list(self.full_cube)

    def _create_packs(self) -> List[DraftPack]:
        """Crea i pacchetti per un singolo round di draft."""
        packs = []
        cards_needed = self.num_players * self.pack_size
        if len(self.remaining_cards) < cards_needed:
            raise ValueError(f"Carte insufficienti nel cubo ({len(self.remaining_cards)}) per un altro round ({cards_needed} necessarie).")
        
        random.shuffle(self.remaining_cards)
        
        for i in range(self.num_players):
            pack_cards = [self.remaining_cards.pop() for _ in range(self.pack_size)]
            packs.append(DraftPack(cards=pack_cards))
        return packs

    def run_draft(self, verbose: bool = False) -> Dict[int, Player]:
        """Esegue l'intera simulazione del draft."""
        if self.logger:
            self.logger.start_draft(self.draft_id)
                
        for pack_number in range(1, self.num_packs + 1):
            if verbose: print(f"\n--- Inizio Round {pack_number}/{self.num_packs} ---")
            
            current_packs = self._create_packs()
            
            for pick_number in range(1, self.pack_size + 1):
                next_packs = [None] * self.num_players
                
                for i, player in enumerate(self.players):
                    bot = self.bots[i]
                    pack_for_player = current_packs[i]
                    
                    pack_before_pick = DraftPack(list(pack_for_player.cards))
                    pool_before_pick = list(player.pool)
                    
                    chosen_card = bot.pick(pack_for_player, pack_number, pick_number)
                    pack_for_player.remove_card(chosen_card)
                    
                    if self.logger:
                        self.logger.log_pick(
                            draft_id=self.draft_id, player_id=player.player_id,
                            pack_num=pack_number, pick_num=pick_number,
                            pack=list(pack_before_pick.cards),
                            pool=pool_before_pick,
                            choice=chosen_card
                        )
                    
                    player.add_to_pool(chosen_card)
                    
                    pass_direction = 1 if pack_number % 2 != 0 else -1
                    pass_to_index = (i - pass_direction) % self.num_players
                    next_packs[pass_to_index] = pack_for_player
                
                current_packs = next_packs

        if self.logger:
            self.logger.save_draft_log(self.draft_id)

        if verbose: print(f"\n--- FINE DRAFT #{self.draft_id} ---\n")
        return {p.player_id: p for p in self.players}