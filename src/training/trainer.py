import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from pathlib import Path
from tqdm import tqdm

class Trainer:
    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        learning_rate: float = 1e-4,
        device: str = 'cpu',
        save_dir: Path = Path("models/experiments") # Rinominato per chiarezza
    ):
        self.model = model.to(device)
        self.train_loader = train_loader
        self.device = device
        self.save_dir = save_dir
        
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
        
        print(f"Trainer inizializzato. Modelli verranno salvati in: '{self.save_dir}'.")

    def train_epoch(self, epoch_num: int) -> float:
        self.model.train()
        total_loss = 0.0
        
        progress_bar = tqdm(self.train_loader, desc=f"Epoch {epoch_num+1}")
        
        for batch_input, batch_target in progress_bar:
            pack = batch_input['pack'].to(self.device)
            pool = batch_input['pool'].to(self.device)
            pick_numbers = batch_input['pick_number'].to(self.device)
            target = batch_target.to(self.device)
            
            self.optimizer.zero_grad()
            
            scores = self.model(pack, pool, pick_numbers)
            
            loss = self.criterion(scores, target)
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
            progress_bar.set_postfix(loss=f"{loss.item():.4f}")
            
        return total_loss / len(self.train_loader)

    def train(self, num_epochs: int):
        """Esegue il ciclo di addestramento completo per N epoche."""
        print(f"\n--- Inizio Addestramento per {num_epochs} epoche ---")
        
        for epoch in range(num_epochs):
            avg_epoch_loss = self.train_epoch(epoch)
            print(f"Fine Epoch {epoch+1}/{num_epochs} - Loss media: {avg_epoch_loss:.4f}")
            
            checkpoint_path = self.save_dir / f"model_epoch_{epoch+1}.pth"
            torch.save(self.model.state_dict(), str(checkpoint_path)) # Usiamo str() per sicurezza
            print(f"Checkpoint salvato in: {checkpoint_path}")
            
        print("\n--- Addestramento Completato ---")
        
        # Salviamo il modello finale come un file, non una cartella
        final_model_path = self.save_dir / "model_final.pth"
        torch.save(self.model.state_dict(), str(final_model_path))
        print(f"Modello finale salvato in: {final_model_path}")