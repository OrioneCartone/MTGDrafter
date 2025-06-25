import torch
from torch.utils.data import Dataset, DataLoader
# MODIFICA: Importa la funzione pad_sequence
from torch.nn.utils.rnn import pad_sequence
from pathlib import Path
import json
from typing import List, Dict, Tuple

# MODIFICA: Importa le costanti strutturali e la configurazione separatamente
from src.utils.constants import FEATURE_SIZE
from src.utils.config_loader import CONFIG

# MODIFICA: Prendi le dimensioni massime dalla configurazione, non più da constants.py
MAX_PACK_SIZE = CONFIG['model']['max_pack_size']
MAX_POOL_SIZE = CONFIG['model']['max_pool_size']

class DraftLogDataset(Dataset):
    """
    Carica i log di draft da una cartella, li processa e li serve al DataLoader.
    """
    def __init__(self, logs_dir: Path):
        self.log_files = sorted(list(logs_dir.glob("*.json")))
        if not self.log_files:
            raise FileNotFoundError(f"Nessun file di log trovato in {logs_dir}")
        
        self.samples = []
        for log_file in self.log_files:
            with open(log_file, 'r') as f:
                log_data = json.load(f)
                for pick in log_data['picks']:
                    self.samples.append({
                        "pack": pick['pack'],
                        "pool": pick['pool'],
                        "choice_index": pick['choice_index'],
                        "pack_num": pick['pack_num'],
                        "pick_num": pick['pick_num']
                    })

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Dict:
        return self.samples[idx]


def custom_collate_fn(batch: List[Dict]) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    Funzione personalizzata per il DataLoader che gestisce il padding.
    """
    # Padding per i pack. Un pack non dovrebbe mai essere vuoto durante un pick valido.
    packs_padded = pad_sequence(
        [torch.tensor(item['pack'], dtype=torch.float32) for item in batch], 
        batch_first=True, 
        padding_value=0.0
    )

    # MODIFICA: Gestisce correttamente i pool vuoti.
    # All'inizio di un draft, il pool è una lista vuota [].
    # torch.tensor([]) crea un tensore 1D, causando un errore di dimensione.
    # Creiamo esplicitamente un tensore 2D di forma [0, FEATURE_SIZE] per i pool vuoti.
    pools_list = [
        torch.tensor(item['pool'], dtype=torch.float32) if item['pool'] 
        else torch.empty(0, FEATURE_SIZE, dtype=torch.float32) 
        for item in batch
    ]
    pools_padded = pad_sequence(pools_list, batch_first=True, padding_value=0.0)

    # Assicura che il tensore dei pick numbers sia 2D (batch_size, 1).
    pick_numbers = torch.tensor([[item['pick_num']] for item in batch], dtype=torch.long)
    
    # MODIFICA: Usa la chiave corretta 'choice_index' come definito nel Dataset.
    choices = torch.tensor([item['choice_index'] for item in batch], dtype=torch.long)
    
    return packs_padded, pools_padded, pick_numbers, choices
