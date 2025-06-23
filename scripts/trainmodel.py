from pathlib import Path
import sys
import torch
from torch.utils.data import DataLoader

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

# --- MODIFICA 1: Importa la configurazione e le costanti necessarie ---
from src.utils.config_loader import CONFIG
from src.utils.constants import FEATURE_SIZE
from src.data.loaders import DraftLogDataset, custom_collate_fn
from src.models.transformerdrafter import TransformerDrafter
from src.training.trainer import Trainer

# --- MODIFICA 2: I percorsi e i parametri sono ora presi dal file di configurazione ---
paths_config = CONFIG['paths']
train_config = CONFIG['training']
model_config = CONFIG['model']

LOGS_DIR = PROJECT_ROOT / paths_config['logs_dir']
MODEL_SAVE_DIR = PROJECT_ROOT / paths_config['model_save_dir']

def main():
    """Addestra il modello Transformer usando la configurazione centralizzata."""
    print("--- Avvio Script di Addestramento (da config.yaml) ---")
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
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
    # --- MODIFICA 3: Inizializza il modello con i parametri dalla config ---
    model = TransformerDrafter(
        feature_size=FEATURE_SIZE,
        embed_dim=model_config['embed_dim'],
        hidden_dim=model_config['hidden_dim'],
        n_heads=model_config['n_heads'],
        n_layers=model_config['n_layers'],
        dropout=model_config['dropout']
    ).to(device)
    
    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Modello creato. Parametri totali: {total_params:,}")
    
    print("Inizializzazione del trainer...")
    trainer = Trainer(
        model=model, 
        train_loader=train_loader, 
        learning_rate=train_config['learning_rate'], # Usa la config
        device=device,
        save_dir=MODEL_SAVE_DIR
    )
    
    print(f"--- Inizio Addestramento per {train_config['num_epochs']} epoche ---")
    trainer.train(num_epochs=train_config['num_epochs']) # Usa la config
    print("--- Addestramento Completato ---")

if __name__ == '__main__':
    main()
