from pathlib import Path
import sys
import torch
from torch.utils.data import DataLoader

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.data.loaders import DraftLogDataset, custom_collate_fn
from src.models.policy_network import PolicyNetwork
from src.training.trainer import Trainer
from src.utils.constants import FEATURE_SIZE

# --- Configurazione del Training (Pauper Generalist) ---
LOGS_DIR = PROJECT_ROOT / "data" / "processed" / "pauper_generalist_logs"
MODEL_SAVE_DIR = PROJECT_ROOT / "models" / "experiments" / "pauper_generalist_v1"

# Hyperparameters
BATCH_SIZE = 128 # Possiamo aumentarlo un po' se abbiamo più dati
LEARNING_RATE = 1e-4
NUM_EPOCHS = 10

def main():
    """Addestra il modello Pauper Generalist."""
    print("--- Avvio Script di Addestramento (Pauper Generalist) ---")
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Dispositivo di addestramento: {device}")
    
    print("Caricamento del dataset...")
    dataset = DraftLogDataset(logs_dir=LOGS_DIR)
    train_loader = DataLoader(
        dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        collate_fn=custom_collate_fn,
        num_workers=4,
        pin_memory=True
    )
    print(f"Dataset caricato con {len(dataset)} campioni.")
    
    model = PolicyNetwork(feature_size=FEATURE_SIZE)
    
    trainer = Trainer(
        model=model,
        train_loader=train_loader,
        learning_rate=LEARNING_RATE,
        device=device,
        model_dir=MODEL_SAVE_DIR
    )
    
    trainer.train(num_epochs=NUM_EPOCHS)

if __name__ == '__main__':
    main()
