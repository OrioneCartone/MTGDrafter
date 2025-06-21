from dataclasses import dataclass, field
from typing import List, Dict

# Usiamo i dataclass per creare oggetti che contengono dati in modo pulito.
# Sono come delle "struct" in altri linguaggi.

@dataclass
class Card:
    """Rappresentazione semplice di una carta di Magic."""
    name: str
    # In futuro aggiungeremo qui altri dati: colori, tipo, ecc.
    # Per ora, il nome è sufficiente.
    details: Dict # Conterrà il JSON completo da Scryfall

@dataclass
class DraftPack:
    """Rappresenta una busta di carte."""
    cards: List[Card]

@dataclass
class Player:
    """Rappresenta un giocatore (o bot) nel draft."""
    player_id: int
    # Il "pool" sono le carte che il giocatore ha già draftato
    pool: List[Card] = field(default_factory=list)

    def add_to_pool(self, card: Card):
        self.pool.append(card)
