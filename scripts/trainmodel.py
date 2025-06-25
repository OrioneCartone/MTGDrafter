from pathlib import Path
import sys
import torch
from torch.utils.data import DataLoader

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.utils.config_loader import CONFIG
from src.utils.constants import FEATURE_SIZE
from src.data.loaders import DraftLogDataset, custom_collate_fn
from src.models.transformerdrafter import TransformerDrafter
from src.training.trainer import Trainer

def main():
    """Funzione principale per l'addestramento del modello."""
    print("--- Avvio Script di Addestramento (da config.yaml) ---")
    
    # Carica le configurazioni
    paths_config = CONFIG['paths']
    model_config = CONFIG['model']
    train_config = CONFIG['training']

    # MODIFICA: Usa le chiavi corrette da config.yaml
    LOGS_DIR = PROJECT_ROOT / paths_config['log_output_dir']
    SAVE_DIR = PROJECT_ROOT / paths_config['model_save_dir']

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Dispositivo di addestramento: {device}")
    
    print("Caricamento del dataset...")
    dataset = DraftLogDataset(logs_dir=LOGS_DIR)
    train_loader = DataLoader(
        dataset, 
        batch_size=train_config['batch_size'], # Usa la config
        shuffle=True,
        collate_fn=custom_collate_fn, 
        num_workers=2, 
        pin_memory=True
    )
    print(f"Dataset caricato con {len(dataset)} campioni.")
    
    print("Inizializzazione del modello TransformerDrafter...")
    # MODIFICA: Passa il dizionario di configurazione direttamente al modello.
    model = TransformerDrafter(
        config=model_config,
        feature_size=FEATURE_SIZE
    ).to(device)
    
    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Modello creato. Parametri totali: {total_params:,}")
    
    print("Inizializzazione del trainer...")
    trainer = Trainer(
        model=model, 
        train_loader=train_loader, 
        learning_rate=train_config['learning_rate'], # Usa la config
        device=device,
        save_dir=SAVE_DIR # Correzione del typo da MODEL_SAVE_DIR a SAVE_DIR
    )
    
    print(f"--- Inizio Addestramento per {train_config['num_epochs']} epoche ---")
    trainer.train(num_epochs=train_config['num_epochs']) # Usa la config
    print("--- Addestramento Completato ---")

if __name__ == '__main__':
    main()
