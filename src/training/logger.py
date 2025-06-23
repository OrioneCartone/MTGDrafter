import json
from pathlib import Path
from typing import List, Dict, Any
import time

from src.environment.draft import Card
from src.features.cardencoders import CardEncoder

class DraftLogger:
    """
    Registra gli eventi di un draft in un formato strutturato (JSON)
    per l'addestramento del modello.
    """
    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.encoder = CardEncoder()
        self._current_draft_data: Dict[Any, Dict] = {}

    def start_draft(self, draft_id: Any):
        """Inizializza la struttura dati per un nuovo log di draft."""
        if draft_id not in self._current_draft_data:
            self._current_draft_data[draft_id] = {
                "draft_id": draft_id,
                "picks": []  # <-- Ecco la chiave che mancava!
            }

    def log_pick(self, draft_id: Any, player_id: int, pack_num: int, pick_num: int, pack: List[Card], pool: List[Card], choice: Card):
        """Registra un singolo evento di pick, convertendo le carte in vettori."""
        if draft_id not in self._current_draft_data:
            self.start_draft(draft_id)

        try:
            choice_index = pack.index(choice)
        except ValueError:
            choice_index = next((i for i, c in enumerate(pack) if c.name == choice.name), -1)
        
        if choice_index == -1: return

        pack_vectors = [self.encoder.encode_card(c.details) for c in pack]
        pool_vectors = [self.encoder.encode_card(c.details) for c in pool]

        pick_data = {
            "player_id": player_id,
            "pack_num": pack_num,
            "pick_num": pick_num,
            "pack": pack_vectors,
            "pool": pool_vectors,
            "choice_index": choice_index
        }
        self._current_draft_data[draft_id]["picks"].append(pick_data)

    def save_draft_log(self, draft_id: Any):
        """Salva il log del draft completato in un file JSON e lo rimuove dalla memoria."""
        if draft_id in self._current_draft_data:
            log_path = self.log_dir / f"draft_log_{draft_id}.json"
            with open(log_path, 'w', encoding='utf-8') as f:
                json.dump(self._current_draft_data[draft_id], f, indent=2)
            del self._current_draft_data[draft_id]

