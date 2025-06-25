import torch
import torch.nn as nn
import torch.nn.functional as F
from ..utils.constants import FEATURE_SIZE


class PolicyNetwork(nn.Module):
    """
    Una rete neurale che prende lo stato di un draft (pack e pool)
    e produce un punteggio per ogni carta nel pack.
    """
    def __init__(self, feature_size: int = FEATURE_SIZE, embedding_dim: int = 64, hidden_dim: int = 128):
        super().__init__()
        """
        Inizializza i layer della rete.
        
        Args:
            feature_size (int): La dimensione del vettore di feature di una carta (14 nel nostro caso).
            embedding_dim (int): Una dimensione intermedia per processare le carte.
            hidden_dim (int): La dimensione dei layer nascosti.
        """
        super().__init__()
        self.feature_size = feature_size
        
        # Un layer per processare il riassunto del pool
        self.pool_processor = nn.Sequential(
            nn.Linear(feature_size, embedding_dim),
            nn.ReLU()
        )
        
        # Un layer per processare ogni carta del pack
        self.pack_card_processor = nn.Sequential(
            nn.Linear(feature_size, embedding_dim),
            nn.ReLU()
        )
        
        # I layer finali che combinano le informazioni e producono il punteggio
        # L'input sarà la concatenazione di (pool_embedding + pack_card_embedding)
        self.scorer = nn.Sequential(
            nn.Linear(embedding_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1) # Output finale: un singolo punteggio
        )

    def forward(self, pack: torch.Tensor, pool: torch.Tensor) -> torch.Tensor:
        """
        Il passaggio "forward" che definisce come i dati fluiscono attraverso la rete.
        
        Args:
            pack (torch.Tensor): Tensore dei pack. Dim: [batch_size, max_pack_size, feature_size]
            pool (torch.Tensor): Tensore dei pool. Dim: [batch_size, max_pool_size, feature_size]
            
        Returns:
            torch.Tensor: Un tensore di punteggi. Dim: [batch_size, max_pack_size]
        """
        batch_size = pack.shape[0]
        max_pack_size = pack.shape[1]
        
        # --- 1. Riassumere il pool ---
        # Calcoliamo la media dei vettori delle carte nel pool per ogni elemento del batch.
        # Aggiungiamo una piccola costante (1e-6) per evitare divisioni per zero se il pool è vuoto.
        num_cards_in_pool = (pool.sum(dim=2) != 0).sum(dim=1).unsqueeze(-1)
        pool_summary = pool.sum(dim=1) / (num_cards_in_pool + 1e-6)
        
        # Processiamo il riassunto del pool
        pool_embedding = self.pool_processor(pool_summary) # -> [batch_size, embedding_dim]
        
        # Espandiamo il pool_embedding per poterlo concatenare con ogni carta del pack
        # -> [batch_size, max_pack_size, embedding_dim]
        pool_embedding_expanded = pool_embedding.unsqueeze(1).expand(-1, max_pack_size, -1)
        
        # --- 2. Processare le carte del pack ---
        # Applichiamo il processore a ogni carta del pack
        # -> [batch_size, max_pack_size, embedding_dim]
        pack_card_embeddings = self.pack_card_processor(pack)
        
        # --- 3. Combinare e calcolare i punteggi ---
        # Concateniamo le informazioni del pool e di ogni carta del pack
        # -> [batch_size, max_pack_size, embedding_dim * 2]
        combined_features = torch.cat([pool_embedding_expanded, pack_card_embeddings], dim=2)
        
        # Applichiamo lo scorer a ogni set di feature combinate
        # -> [batch_size, max_pack_size, 1]
        scores = self.scorer(combined_features)
        
        # Rimuoviamo l'ultima dimensione per ottenere [batch_size, max_pack_size]
        return scores.squeeze(-1)

# Blocco di test per verificare che il modello funzioni
if __name__ == '__main__':
    # Creiamo dati finti con le stesse dimensioni dei nostri batch
    batch_size = 4
    max_pack_size = 15
    max_pool_size = 45
    feature_size = 15
    
    fake_pack = torch.randn(batch_size, max_pack_size, feature_size)
    fake_pool = torch.randn(batch_size, max_pool_size, feature_size)
    
    # Creiamo un'istanza del modello
    model = PolicyNetwork(feature_size=feature_size)
    
    # Facciamo un passaggio forward
    output_scores = model(fake_pack, fake_pool)
    
    print("--- Test del Modello ---")
    print(f"Input pack shape:  {fake_pack.shape}")
    print(f"Input pool shape:  {fake_pool.shape}")
    print(f"Output scores shape: {output_scores.shape}") # Dovrebbe essere [batch_size, max_pack_size]
    print("\n✅ Test del modello completato con successo!")

