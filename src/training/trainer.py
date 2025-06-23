import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from pathlib import Path
from tqdm import tqdm

class Trainer:
    """
    Gestisce il ciclo di addestramento e salvataggio del modello.
    """
    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        learning_rate: float = 1e-4,
        device: str = 'cpu',
        save_dir: Path = Path("models/experiments") # Rinominato per chiarezza
    ):
        self.model = model
        self.train_loader = train_loader
        self.optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
        self.criterion = nn.CrossEntropyLoss() # Adatto per problemi di classificazione (scegliere una carta tra N)
        self.device = device
        self.save_dir = save_dir # MODIFICA: Assicurati che venga salvato
        self.save_dir.mkdir(parents=True, exist_ok=True) # Crea la cartella se non esiste

        print(f"Trainer inizializzato. Modelli verranno salvati in: '{self.save_dir}'.")

    def train_epoch(self, epoch_num: int) -> float:
        """Esegue una singola epoca di addestramento."""
        self.model.train()
        total_loss = 0.0
        progress_bar = tqdm(self.train_loader, desc=f"Epoch {epoch_num}", leave=False)
        
        # MODIFICA: Unpack corretto dei 4 tensori restituiti dal DataLoader
        for packs, pools, pick_numbers, choices in progress_bar:
            # Sposta tutti i tensori sul dispositivo corretto
            packs = packs.to(self.device)
            pools = pools.to(self.device)
            pick_numbers = pick_numbers.to(self.device)
            choices = choices.to(self.device) # Questo è il target (y)

            self.optimizer.zero_grad()
            
            # Passa i 3 tensori di input al modello per ottenere i punteggi (logits)
            scores = self.model(packs, pools, pick_numbers) 
            
            # Calcola la loss tra i punteggi predetti e la scelta reale (l'indice della carta scelta)
            loss = self.criterion(scores, choices)
            loss.backward()
            self.optimizer.step()

            total_loss += loss.item()
            progress_bar.set_postfix(loss=loss.item())
            
        return total_loss / len(self.train_loader)

    def train(self, num_epochs: int):
        """Esegue il ciclo di addestramento completo per N epoche."""
        print(f"\n--- Inizio Addestramento per {num_epochs} epoche ---")
        
        for epoch in range(1, num_epochs + 1):
            avg_epoch_loss = self.train_epoch(epoch)
            print(f"Epoch {epoch}/{num_epochs} - Loss media: {avg_epoch_loss:.4f}")
            
            # Salva il modello alla fine di ogni epoca
            self.save_model(epoch)

        print("\n--- Addestramento Completato ---")
        
        # Salviamo il modello finale come un file, non una cartella
        final_model_path = self.save_dir / "model_final.pth"
        torch.save(self.model.state_dict(), str(final_model_path))
        print(f"Modello finale salvato in: {final_model_path}")

    def save_model(self, epoch: int):
        """Salva lo stato del modello."""
        save_path = self.save_dir / f"transformer_drafter_epoch_{epoch}.pth"
        torch.save(self.model.state_dict(), save_path)
        print(f"Modello salvato in: {save_path}")