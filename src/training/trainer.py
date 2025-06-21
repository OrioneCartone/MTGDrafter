import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from pathlib import Path
from tqdm import tqdm

from ..models.policy_network import PolicyNetwork

class Trainer:
    """
    Gestisce il ciclo di addestramento completo per la PolicyNetwork.
    """
    def __init__(
        self,
        model: PolicyNetwork,
        train_loader: DataLoader,
        learning_rate: float = 1e-4,
        device: str = 'cpu',
        model_dir: Path = Path("models/experiments")
    ):
        self.model = model.to(device)
        self.train_loader = train_loader
        self.device = device
        self.model_dir = model_dir
        
        # Creiamo la directory per salvare i modelli, se non esiste
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        # Loss Function: CrossEntropyLoss è perfetta per problemi di classificazione
        # "multi-classe", come il nostro ("scegli la carta giusta tra N opzioni").
        # Combina una Softmax (per trasformare i punteggi in probabilità) e una
        # Negative Log-Likelihood Loss.
        self.criterion = nn.CrossEntropyLoss()
        
        # Optimizer: AdamW è una scelta moderna e robusta che funziona bene
        # per la maggior parte dei problemi di deep learning.
        self.optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
        
        print(f"Trainer inizializzato. Modello su dispositivo: '{self.device}'.")

    def train_epoch(self, epoch_num: int) -> float:
        """Esegue un'epoca completa di addestramento."""
        self.model.train() # Mette il modello in modalità "training"
        total_loss = 0.0
        
        # Usiamo tqdm per una barra di progresso sull'epoca
        progress_bar = tqdm(self.train_loader, desc=f"Epoch {epoch_num+1}")
        
        for batch_input, batch_target in progress_bar:
            # Sposta i dati sul dispositivo corretto (CPU o GPU)
            pack = batch_input['pack'].to(self.device)
            pool = batch_input['pool'].to(self.device)
            target = batch_target.to(self.device)
            
            # 1. Azzera i gradienti dall'iterazione precedente
            self.optimizer.zero_grad()
            
            # 2. Forward pass: ottieni i punteggi dal modello
            scores = self.model(pack, pool)
            
            # 3. Calcola la loss
            # La loss misura quanto i punteggi del modello si discostano
            # dalla scelta corretta (il target).
            loss = self.criterion(scores, target)
            
            # 4. Backward pass: calcola i gradienti
            loss.backward()
            
            # 5. Optimizer step: aggiorna i pesi del modello
            self.optimizer.step()
            
            total_loss += loss.item()
            
            # Aggiorna la descrizione della barra di progresso
            progress_bar.set_postfix(loss=f"{loss.item():.4f}")
            
        return total_loss / len(self.train_loader)

    def train(self, num_epochs: int):
        """Esegue il ciclo di addestramento completo per N epoche."""
        print(f"\n--- Inizio Addestramento per {num_epochs} epoche ---")
        
        for epoch in range(num_epochs):
            avg_epoch_loss = self.train_epoch(epoch)
            print(f"Fine Epoch {epoch+1}/{num_epochs} - Loss media: {avg_epoch_loss:.4f}")
            
            # Salva un checkpoint del modello alla fine di ogni epoca
            checkpoint_path = self.model_dir / f"policy_net_epoch_{epoch+1}.pth"
            torch.save(self.model.state_dict(), checkpoint_path)
            print(f"Checkpoint salvato in: {checkpoint_path}")
            
        print("\n--- Addestramento Completato ---")
        final_model_path = self.model_dir / "policy_net_final.pth"
        torch.save(self.model.state_dict(), final_model_path)
        print(f"Modello finale salvato in: {final_model_path}")

