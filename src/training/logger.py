import json
from pathlib import Path
from typing import List
import time

from ..environment.draft import Card
from ..features.cardencoders import CardEncoder

class DraftLogger:
    """
    Gestisce il salvataggio dei dati di un draft in un formato strutturato,
    pronto per essere usato per l'addestramento.
    """
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.encoder = CardEncoder()
        print(f"Logger inizializzato. I log verranno salvati in: {self.output_dir}")

    def log_pick(self, draft_id: int, player_id: int, pack_num: int, pick_num: int, pack: List[Card], pool: List[Card], choice: Card):
        """
        Salva una singola decisione di draft convertendo le carte in vettori.
        """
        # Per evitare di ricalcolare il vettore della carta scelta
        choice_vector = self.encoder.encode_card(choice.details)
        
        pack_vectors = []
        for card in pack:
            # Assicuriamoci che la carta scelta sia presente nel pack (per coerenza)
            if card.details['id'] == choice.details['id']:
                pack_vectors.append(choice_vector)
            else:
                pack_vectors.append(self.encoder.encode_card(card.details))

        log_entry = {
            'draft_id': draft_id,
            'player_id': player_id,
            'pack_num': pack_num,
            'pick_num': pick_num,
            'pack_vectors': pack_vectors,
            'pool_vectors': [self.encoder.encode_card(c.details) for c in pool],
            'choice_vector': choice_vector,
        }
        
        # Usiamo un timestamp per un nome di file unico
        timestamp = int(time.time() * 1000)
        filename = f"log_{draft_id}_{player_id}_{pack_num}_{pick_num}_{timestamp}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(log_entry, f)

