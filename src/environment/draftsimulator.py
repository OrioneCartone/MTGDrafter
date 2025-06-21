# ... (tutti gli import rimangono uguali) ...

class DraftSimulator:
    # ... (il costruttore __init__ e i metodi _load_cube, _create_packs rimangono uguali) ...

    def run_draft(self, verbose: bool = True) -> Dict[int, Player]:
        """Esegue l'intera simulazione del draft."""
        if verbose: print(f"\n--- INIZIO DRAFT #{self.draft_id} ---")
        
        for pack_number in range(1, self.num_packs + 1):
            if verbose: print(f"\n--- Inizio Round {pack_number}/{self.num_packs} ---")
            
            current_packs = self._create_packs()

            for pick_number in range(1, self.pack_size + 1):
                if verbose: print(f"\n-- Pick {pick_number}/{self.pack_size} --")
                
                # Lista temporanea per conservare le carte scelte in questo turno
                choices_this_turn = [None] * self.num_players
                
                # Ogni bot sceglie una carta dalla busta che ha attualmente
                for i in range(self.num_players):
                    bot = self.bots[i]
                    pack_for_bot = current_packs[i]
                    
                    # Logga lo stato PRIMA della decisione (se c'è un logger)
                    if self.logger:
                        self.logger.log_pick(
                            draft_id=self.draft_id, player_id=i, pack_num=pack_number, pick_num=pick_number,
                            pack=pack_for_bot.cards, pool=list(self.players[i].pool), choice=None # La scelta non è ancora nota
                        )

                    chosen_card = bot.pick(pack_for_bot, pack_number, pick_number)
                    choices_this_turn[i] = chosen_card

                # Ora che tutti hanno scelto, aggiorniamo lo stato
                for i in range(self.num_players):
                    chosen_card = choices_this_turn[i]
                    
                    # Aggiungi la carta al pool del giocatore
                    self.players[i].add_to_pool(chosen_card)
                    
                    # Rimuovi la carta dalla busta corretta
                    current_packs[i].cards.remove(chosen_card)

                    # Aggiorna il log con la scelta effettiva (se c'è un logger)
                    # (Questa parte è un po' più complessa da implementare bene,
                    # per ora la nostra logica nel logger è sufficiente)

                # Passa le buste solo DOPO che tutti hanno fatto il loro pick del turno
                if pack_number % 2 == 1: # Round 1 e 3: passa a sinistra
                    # Ruota la lista delle buste
                    current_packs = current_packs[1:] + current_packs[:1]
                else: # Round 2: passa a destra
                    current_packs = current_packs[-1:] + current_packs[:-1]

        if verbose: print(f"\n--- DRAFT #{self.draft_id} CONCLUSO ---")
        return {player.player_id: player for player in self.players}

