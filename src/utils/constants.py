# src/utils/constants.py

# ===================================================================
# KEYWORD UFFICIALI (da Scryfall)
# ===================================================================
# Queste sono le abilità di combattimento e statiche più comuni e impattanti.
KEYWORD_LIST = [
    # Combattimento
    'Deathtouch', 
    'Double strike', 
    'First strike',
    'Trample',
    'Indestructible',
    'Menace',
    'Reach',
    # Evasione
    'Flying',
    'Skulk',        # Difficile da bloccare per creature più forti
    'Prowess',      # Si potenzia giocando non-creature
    # Utilità
    'Vigilance',
    'Lifelink',
    'Haste',
    'Flash',
    'Hexproof',
    'Defender',
    # Abilità legate al mana
    'Convoke',
    'Affinity for artifacts',
    # Abilità di "recursion"
    'Unearth',
    'Encore',
    'Disturb',
]

# ===================================================================
# PATTERN DI ABILITÀ TESTUALI (Cercati nell'Oracle Text)
# ===================================================================
# Qui cerchiamo gli effetti più comuni che definiscono il ruolo di una carta.
# Ogni "chiave" rappresenta un concetto di gioco.
ABILITY_PATTERNS = {
    # --- Vantaggio di Carte ---
    'draw_card': ['draw a card'],
    'draw_multiple_cards': ['draw two cards', 'draw three cards'], # Più specifico e potente
    'cantrip': ['when this enters the battlefield, draw a card'], # La classica "cantrip creature"
    'scry': ['scry'],
    'surveil': ['surveil'],
    'investigate': ['investigate'], # Crea un indizio, che è vantaggio carte differito

    # --- Interazione con l'Avversario (Rimozioni) ---
    'destroy_creature': ['destroy target creature'],
    'exile_permanent': ['exile target'], # Più generico di solo creature
    'damage_to_creature': ['deals', 'damage to target creature'],
    'damage_to_player': ['deals', 'damage to any target', 'damage to target player'], # Sparo/burn
    'return_to_hand': ['return target', 'to its owner\'s hand'], # Bounce effect
    'tap_down': ['tap target creature', 'doesn\'t untap'], # Effetto di "tappare"
    'pacifism': ['enchanted creature can\'t attack or block'], # Aura di Pacifismo
    'discard': ['player discards', 'card'],

    # --- Sinergie e Motori del Mazzo ---
    'mana_ramp': ['add {', '}'], # Genera mana (es. Llanowar Elves)
    'mana_fix': ['add one mana of any color'], # Fissa il mana
    'create_token_1_1': ['create a 1/1'], # Crea pedine piccole
    'create_token_large': ['create a', 'token with power 3 or greater', '4/4', '5/5'], # Crea minacce
    'pump_all': ['creatures you control get'], # Effetto "anthem" o di potenziamento di massa
    'pump_single': ['target creature gets +'], # Trick di combattimento
    'sac_outlet': ['sacrifice a creature:'], # "Sacrifice outlet" per sinergie
    'graveyard_recursion': ['return target creature card from your graveyard'], # Far tornare creature
    'counter_spell': ['counter target', 'spell'],

    # --- Meccaniche Specifiche (utili in Pauper Cube) ---
    'flicker': ['exile another target creature', 'return it to the battlefield'], # Effetto "blink/flicker"
    'storm_count': ['storm'], # Storm
    'threshold_delirium': ['if there are', 'or more', 'in your graveyard'], # Abilità che dipendono dal cimitero
    'artifact_synergy': ['affinity for artifacts', 'metalcraft'],
    'enchantment_synergy': ['whenever you cast an enchantment', 'constellation']
}

# ===================================================================
# CALCOLO DELLA DIMENSIONE FINALE DEL VETTORE
# ===================================================================
OLD_FEATURE_SIZE = 15 # 5 colori + 1 cmc + 7 tipi + 2 p/t
KEYWORD_FEATURE_SIZE = len(KEYWORD_LIST)
ABILITY_FEATURE_SIZE = len(ABILITY_PATTERNS)

FEATURE_SIZE = OLD_FEATURE_SIZE + KEYWORD_FEATURE_SIZE + ABILITY_FEATURE_SIZE

print(f"DEBUG: Nuova dimensione del vettore di feature: {FEATURE_SIZE} ({OLD_FEATURE_SIZE} base + {KEYWORD_FEATURE_SIZE} keyword + {ABILITY_FEATURE_SIZE} abilità)")

# Queste rimangono invariate
MAX_PACK_SIZE = 15
MAX_POOL_SIZE = 45
