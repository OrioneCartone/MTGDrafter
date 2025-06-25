import torch
import torch.nn as nn
from typing import Dict

class TransformerDrafter(nn.Module):
    """
    Un modello Transformer per prevedere la scelta migliore in un draft di Magic.
    Accetta lo stato del pack, del pool e il numero del pick come input.
    """
    def __init__(self, config: Dict, feature_size: int):
        super().__init__()
        self.config = config
        self.d_model = config['d_model']

        self.pack_embedding = nn.Linear(feature_size, self.d_model)
        self.pool_embedding = nn.Linear(feature_size, self.d_model)
        
        # L'embedding è dimensionato per accettare indici fino a max_pack_size.
        # I pick vanno da 1 a 15, quindi abbiamo bisogno di 16 slot (indici 0-15).
        num_pick_embeddings = config['max_pack_size'] + 1
        self.pick_num_embedding = nn.Embedding(
            num_embeddings=num_pick_embeddings, 
            embedding_dim=self.d_model
        )

        self.transformer = nn.Transformer(
            d_model=self.d_model,
            nhead=config['nhead'],
            num_encoder_layers=config['num_encoder_layers'],
            num_decoder_layers=config['num_decoder_layers'],
            dim_feedforward=config['dim_feedforward'],
            dropout=config['dropout'],
            batch_first=True
        )

        self.output_layer = nn.Linear(self.d_model, 1)

    def forward(self, pack_tensor, pool_tensor, pick_number_tensor):
        pack_embedded = self.pack_embedding(pack_tensor)
        pool_embedded = self.pool_embedding(pool_tensor)
        
        valid_indices = torch.clamp(
            pick_number_tensor, 0, self.pick_num_embedding.num_embeddings - 1
        )
        
        # MODIFICA: Rimuovi la chiamata .unsqueeze(1) che causava l'errore di dimensione.
        # L'output dell'embedding è già della forma corretta (batch, 1, d_model).
        pick_embedded = self.pick_num_embedding(valid_indices)
        # --- FINE MODIFICA ---

        # Ora entrambi i tensori sono 3D e possono essere concatenati.
        encoder_input = torch.cat([pool_embedded, pick_embedded], dim=1)
        decoder_input = pack_embedded

        transformer_output = self.transformer(src=encoder_input, tgt=decoder_input)
        scores = self.output_layer(transformer_output).squeeze(-1)

        return scores
