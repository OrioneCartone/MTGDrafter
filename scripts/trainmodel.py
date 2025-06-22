from pathlib import Path
import sys
import torch
from torch.utils.data import DataLoader

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.data.loaders import DraftLogDataset, custom_collate_fn
# --- MODIFICA 1: Importa il nuovo modello ---
from src.models.transformerdrafter import TransformerDrafter
from src.training.trainer import Trainer
from src.utils.constants import FEATURE_SIZE

# --- Configurazione del Training (Esperimento Transformer) ---
LOGS_DIR = PROJECT_ROOT / "data" / "processed" / "pauper_generalist_logs"
# --- MODIFICA 2: Salviamo in una nuova cartella per non sovrascrivere ---
MODEL_SAVE_DIR = PROJECT_ROOT / "models" / "experiments" / "transformer_v1" / "model_final.pth"

# Hyperparameters
BATCH_SIZE = 64 # Riduciamo un po' il batch size, i transformer usano più memoria
LEARNING_RATE = 5e-5 # I transformer spesso beneficiano di un learning rate più basso
NUM_EPOCHS = 10
def main():
    """Addestra il modello Transformer."""
    print("--- Avvio Script di Addestramento (TransformerDrafter v1) ---")
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Dispositivo di addestramento: {device}")
    
    print("Caricamento del dataset...")
    dataset = DraftLogDataset(logs_dir=LOGS_DIR)
    train_loader = DataLoader(
        dataset, batch_size=BATCH_SIZE, shuffle=True,
        collate_fn=custom_collate_fn, num_workers=2, pin_memory=True
    )
    print(f"Dataset caricato con {len(dataset)} campioni.")
    
    print("Inizializzazione del modello TransformerDrafter...")
    model = TransformerDrafter(
        feature_size=FEATURE_SIZE,
        embed_dim=128,    # Questo è il nostro 'd_model' concettuale
        hidden_dim=256
    )
    
    # Contiamo i parametri per curiosità
    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Modello creato. Parametri totali: {total_params:,}")
    
    trainer = Trainer(
        model=model, train_loader=train_loader, learning_rate=LEARNING_RATE,
        device=device, model_dir=MODEL_SAVE_DIR
    )
    
    trainer.train(num_epochs=NUM_EPOCHS)

if __name__ == '__main__':
    main()
