from pathlib import Path
import sys
import torch
from torch.utils.data import DataLoader

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.data.loaders import DraftLogDataset, custom_collate_fn
from src.models.policy_network import PolicyNetwork
from src.training.trainer import Trainer

# --- Configurazione del Training ---
# Parametri che possiamo modificare per i nostri esperimenti
LOGS_DIR = PROJECT_ROOT / "data" / "processed" / "draft_logs"
MODEL_SAVE_DIR = PROJECT_ROOT / "models" / "experiments" / "run_01"

# Hyperparameters
BATCH_SIZE = 64
LEARNING_RATE = 1e-4
NUM_EPOCHS = 10
FEATURE_SIZE = 14 # Assicurati che corrisponda alla lunghezza reale del tuo vettore

def main():
    """Script principale per orchestrare l'addestramento del modello."""
    print("--- Avvio Script di Addestramento ---")
    
    # Imposta il dispositivo (usa la GPU se disponibile, altrimenti la CPU)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Dispositivo di addestramento: {device}")
    
    # 1. Preparare il DataLoader
    print("Caricamento del dataset...")
    dataset = DraftLogDataset(logs_dir=LOGS_DIR)
    train_loader = DataLoader(
        dataset,
        batch_size=BATCH_SIZE,
        shuffle=True, # Mischiare i dati è fondamentale per un buon training
        collate_fn=custom_collate_fn,
        num_workers=4, # Usa più processi per caricare i dati (se possibile)
        pin_memory=True # Ottimizzazione per GPU
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
