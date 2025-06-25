# Questo file definisce le costanti strutturali del progetto.
# Gli iperparametri e i percorsi sono definiti in /config/config.yaml

# ========================== KEYWORD UFFICIALI ==========================
KEYWORD_LIST = [
    'Deathtouch', 'Double strike', 'First strike', 'Trample', 'Indestructible',
    'Menace', 'Reach', 'Flying', 'Skulk', 'Shadow', 'Vigilance',
    'Lifelink', 'Haste', 'Flash', 'Hexproof', 'Defender', 'Prowess', 'Convoke',
    'Affinity for artifacts', 'Improvise', 'Unearth', 'Encore', 'Disturb',
    'Flashback', 'Dredge', 'Persist', 'Madness', 'Suspend', 'Vanishing',
    'Modular', 'Cycling','Delve', 'Kicker', 'Buyback', 'Entwine', 'Bestow', 'Equip', 'Ward'
]

# ========================== PATTERN DI ABILITÀ TESTUALI ==========================
ABILITY_PATTERNS = {
    # A) Vantaggio di Risorse
    'draw_card': ['draw a card'],
    'draw_multiple_cards': ['draw two cards', 'draw three cards'],
    'etb': ['when this creature enters'],
    'looting_effect': ['draw a card, then discard a card'],
    'rummaging_effect': ['discard a card, then draw a card'],
    'investigate': ['investigate'],
    'scry': ['scry '],
    'scry_top': ['look at the top', 'cards of your library'],
    'scry_bottom': ['put that card on the bottom of your library'],
    'surveil': ['surveil '],
    'explore': ['explore'],
    'treasure_token': ['create a Treasure token'],
    'clue_token': ['create a Clue token'],
    'food_token': ['create a Food token'],
    'life_gain': ['you gain', 'life'],
    'graveyard_recursion_creature': ['return target creature card from your graveyard'],
    'graveyard_recursion_any': ['return target', 'from your graveyard'],
    'tutor_basic_land': ['search your library for a basic land card'],

    
    # B) Interazione con l'Avversario
    'destroy_creature': ['destroy target creature'],
    'exile_permanent': ['exile target'],
    'damage_to_any_target': ['deals', 'damage to any target'],
    'return_to_hand_creature': ['return target creature', "to its owner's hand"],
    'tap_down': ['tap target creature.', "doesn't untap"],
    'pacifism_effect': ["can't attack or block"],
    'discard_hand': ['target player discards'],
    'counter_spell_hard': ['counter target spell'],
    'counter_spell_soft': ['counter target', 'unless its controller pays'],
    'board_wipe_damage': ['deals', 'damage to each creature'],
    'edict_effect': ['sacrifices a creature'],

    
    # C) Gestione del Mana
    'mana_dork': ['creature', '{t}: add'],
    'mana_rock': ['artifact', '{t}: add'],
    'mana_ramp_spell': ['search your library for', 'land card', 'put it onto the battlefield'],
    'cost_reduction': ['costs {1} less to cast'],
    'ritual_effect': ['add {r}{r}{r}', 'add {b}{b}{b}'],
    'mana_fix': ['add one mana of any color'],
    
    # D) Motori di Sinergia
    'create_tokens_wide': ['create', '1/1'],
    'create_token_tall': ['create a', 'token with power 3 or greater'],
    'pump_all_static': ['creatures you control get +1/+1'],
    'pump_all_temporary': ['creatures you control get +', 'until end of turn'],
    'pump_single_trick': ['target creature gets +'],
    'sac_outlet': ['sacrifice a creature:'],
    'payoff_for_sac': ['whenever you sacrifice', 'whenever a creature you control dies'],
    'spells_matter_payoff': ['whenever you cast a noncreature spell', 'whenever you cast an instant or sorcery'],
    'artifacts_matter_payoff': ['metalcraft'],
    'enchantments_matter_payoff': ['constellation'],
    'blink_flicker_effect': ['exile', 'return it to the battlefield'],
    'lifegain_payoff': ['whenever you gain life'],
    
    # E) Meccaniche Speciali
    'monarch': ['you become the monarch'],
    'initiative': ['you take the initiative'],

    # F) Tipi di Abilità Strutturali (attualmente non usate per pattern matching)
    'has_activated_ability_mana': [], 
    'has_activated_ability_tap': [],
    'has_triggered_ability': []
}

# ========================== CALCOLO DIMENSIONE VETTORE ==========================
# Queste sono costanti derivate dalla struttura dei dati, non iperparametri.
BASE_FEATURE_SIZE = 6 + 1 + 7 + 2  # Colors(6) + CMC(1) + Type(7) + P/T(2) = 16
KEYWORD_FEATURE_SIZE = len(KEYWORD_LIST)
ABILITY_FEATURE_SIZE = len(ABILITY_PATTERNS)

# La dimensione totale è la somma di tutte le parti.
# Questo è l'UNICO punto in cui la dimensione totale viene definita.
FEATURE_SIZE = BASE_FEATURE_SIZE + KEYWORD_FEATURE_SIZE + ABILITY_FEATURE_SIZE
