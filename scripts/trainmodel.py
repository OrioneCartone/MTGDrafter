from pathlib import Path
import sys
import torch
from torch.utils.data import DataLoader

# --- BLOCCO DI CODICE DA AGGIUNGERE ---
# Aggiunge la root del progetto al path di Python per trovare i nostri moduli
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))
# --- FINE BLOCCO DA AGGIUNGERE ---

from src.data.loaders import DraftLogDataset, custom_collate_fn
from src.models.policy_network import PolicyNetwork
from src.training.trainer import Trainer
from src.utils.constants import FEATURE_SIZE # Ora questo import funzionerà

# --- Configurazione del Training ---
LOGS_DIR = PROJECT_ROOT / "data" / "processed" / "draft_logs"
MODEL_SAVE_DIR = PROJECT_ROOT / "models" / "experiments" / "run_01"

# Hyperparameters
BATCH_SIZE = 64
LEARNING_RATE = 1e-4
NUM_EPOCHS = 10
# FEATURE_SIZE è ora importato da constants.py

def main():
    """Script principale per orchestrare l'addestramento del modello."""
    print("--- Avvio Script di Addestramento ---")
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Dispositivo di addestramento: {device}")
    
    # 1. Preparare il DataLoader
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
    print("Dataset caricato.")
    
    # 2. Inizializzare il Modello
    model = PolicyNetwork(feature_size=FEATURE_SIZE)
    
    # 3. Inizializzare il Trainer
    trainer = Trainer(
        model=model,
        train_loader=train_loader,
        learning_rate=LEARNING_RATE,
        device=device,
        model_dir=MODEL_SAVE_DIR
    )
    
    # 4. Avviare l'addestramento
    trainer.train(num_epochs=NUM_EPOCHS)

if __name__ == '__main__':
    main()
