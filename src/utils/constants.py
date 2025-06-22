# src/utils/constants.py

# ===================================================================
# KEYWORD UFFICIALI
# ===================================================================
KEYWORD_LIST = [
    'Deathtouch', 'Double strike', 'First strike', 'Trample', 'Indestructible',
    'Menace', 'Reach', 'Flying', 'Skulk', 'Shadow', 'Horsemanship', 'Vigilance',
    'Lifelink', 'Haste', 'Flash', 'Hexproof', 'Defender', 'Prowess', 'Convoke',
    'Affinity for artifacts', 'Improvise', 'Unearth', 'Encore', 'Disturb',
    'Flashback', 'Dredge', 'Persist', 'Madness', 'Suspend', 'Vanishing',
    'Modular', 'Cycling', 'Kicker', 'Buyback', 'Entwine', 'Bestow', 'Equip', 'Ward'
]

# ===================================================================
# PATTERN DI ABILITÀ TESTUALI
# ===================================================================
ABILITY_PATTERNS = {
    # --- A) Vantaggio di Risorse ---
    'draw_card': ['draw a card'],
    'draw_multiple_cards': ['draw two cards', 'draw three cards'],
    'cantrip_etb': ['when this creature enters the battlefield, draw a card'], # ETB = Enters The Battlefield
    'looting_effect': ['draw a card, then discard a card'], # Pattern esatto per Looting
    'rummaging_effect': ['discard a card, then draw a card'], # Pattern esatto per Rummaging
    'investigate': ['investigate'],
    'scry': ['scry '], # Aggiunto spazio per evitare match con "scryer" etc.
    'surveil': ['surveil '], # Aggiunto spazio
    'explore': ['explore'],
    'graveyard_recursion_creature': ['return target creature card from your graveyard'],
    'graveyard_recursion_any': ['return target', 'from your graveyard'],
    'tutor_basic_land': ['search your library for a basic land card'],
    
    # --- B) Interazione con l'Avversario ---
    'destroy_creature': ['destroy target creature'],
    'exile_permanent': ['exile target'],
    'damage_to_any_target': ['deals', 'damage to any target'],
    'return_to_hand_creature': ['return target creature', "to its owner's hand"],
    'tap_down': ['tap target creature.', "doesn't untap"], # ". " per distinguere da costi
    'pacifism_effect': ["can't attack or block"],
    'discard_hand': ['target player discards'],
    'counter_spell_hard': ['counter target spell'],
    'counter_spell_soft': ['counter target', 'unless its controller pays'],
    'board_wipe_damage': ['deals', 'damage to each creature'],
    'edict_effect': ['sacrifices a creature'],
    
    # --- C) Gestione del Mana ---
    'mana_dork': ['creature', '{t}: add'],
    'mana_rock': ['artifact', '{t}: add'],
    'mana_ramp_spell': ['search for', 'land card', 'put it onto the battlefield'],
    'cost_reduction': ['costs {1} less to cast'], # Reso più specifico
    'ritual_effect': ['add {r}{r}{r}', 'add {b}{b}{b}'],
    'mana_fix': ['add one mana of any color'],
    
    # --- D) Motori di Sinergia e Archetipi ---
    'create_tokens_wide': ['create', '1/1'],
    'create_token_tall': ['create a', 'token with power 3 or greater', '4/4', '5/5', 'X/X'],
    'pump_all_static': ['creatures you control get +1/+1'],
    'pump_all_temporary': ['creatures you control get +', 'until end of turn'],
    'pump_single_trick': ['target creature gets +'],
    'sac_outlet': ['sacrifice a creature:'],
    'payoff_for_sac': ['whenever you sacrifice', 'whenever a creature you control dies'],
    'spells_matter_payoff': ['whenever you cast a noncreature spell', 'whenever you cast an instant or sorcery'],
    'artifacts_matter_payoff': ['metalcraft', 'affinity for artifacts'],
    'enchantments_matter_payoff': ['constellation'],
    'blink_flicker_effect': ['exile', 'return it to the battlefield'],
    'lifegain_payoff': ['whenever you gain life'],
    
    # --- E) Meccaniche Speciali ---
    'monarch': ['you become the monarch'],
    'initiative': ['you take the initiative'],

    # --- F) Tipi di Abilità Strutturali (gestiti da logica speciale) ---
    'has_activated_ability_mana': [], # Abilità attivata che costa mana
    'has_activated_ability_tap': [],  # Abilità attivata che richiede di tappare
    'has_triggered_ability': []     # Abilità innescata (when, whenever, at)
}

# Calcolo finale e corretto
OLD_FEATURE_SIZE = 15 
KEYWORD_FEATURE_SIZE = len(KEYWORD_LIST)
ABILITY_FEATURE_SIZE = len(ABILITY_PATTERNS)
FEATURE_SIZE = OLD_FEATURE_SIZE + KEYWORD_FEATURE_SIZE + ABILITY_FEATURE_SIZE

print(f"DEBUG: Dimensione vettore feature inizializzata a: {FEATURE_SIZE}")

MAX_PACK_SIZE = 15
MAX_POOL_SIZE = 45

# ===================================================================
# IPERPARAMETRI DEL MODELLO
# ===================================================================
# Definiamo l'architettura del nostro modello in un unico posto per coerenza.

MODEL_EMBED_DIM = 128      # Dimensione interna del modello Transformer
MODEL_HIDDEN_DIM = 256     # Dimensione dei layer nascosti nello scorer
MODEL_NHEAD = 4          # Numero di "teste di attenzione" (deve dividere embed_dim)
MODEL_ENCODER_LAYERS = 2 # Numero di strati del Transformer
MODEL_FF_DIM = 256       # Dimensione del feed-forward interno