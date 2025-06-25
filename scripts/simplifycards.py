import json
from pathlib import Path
import sys

# Aggiunge la root del progetto al path per permettere l'import da src
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.utils.config_loader import CONFIG

def simplify_card_database(input_path: Path, output_path: Path):
    """
    Carica un database di carte JSON da Scryfall e lo semplifica,
    mantenendo solo i campi essenziali per il progetto.
    """
    print(f"▶️  Caricamento del database completo da: {input_path}")
    if not input_path.exists():
        print(f"❌ ERRORE: File di input non trovato: {input_path}")
        print("💡 Assicurati di aver eseguito prima lo script 'downloaddata.py'.")
        sys.exit(1)

    with open(input_path, 'r', encoding='utf-8') as f:
        full_database = json.load(f)

    print(f"✅ Trovate {len(full_database)} carte nel database originale.")
    
    simplified_database = []
    # Lista dei campi da mantenere
    fields_to_keep = [
        'name', 'mana_cost', 'cmc', 'type_line', 
        'power', 'toughness', 'oracle_text'
    ]

    for card_data in full_database:
        simplified_card = {}
        
        source_data = card_data
        if 'card_faces' in card_data and card_data.get('card_faces'):
            source_data = card_data['card_faces'][0]
            for field in ['name', 'cmc']:
                 if field in card_data:
                    simplified_card[field] = card_data[field]

        for field in fields_to_keep:
            if field in source_data:
                simplified_card[field] = source_data[field]
        
        if 'name' not in simplified_card and 'name' in card_data:
            simplified_card['name'] = card_data['name']

        if 'name' in simplified_card:
            simplified_database.append(simplified_card)

    print(f"✅ Create {len(simplified_database)} carte semplificate.")
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(simplified_database, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Database semplificato salvato con successo in: {output_path}")

def main():
    """
    Script principale per eseguire la semplificazione del database.
    Legge sempre il file originale e scrive quello semplificato.
    """
    print("\n--- Avvio Script di Semplificazione Database Carte ---")
    
    # MODIFICA CHIAVE: Non leggiamo più il percorso dal config per evitare il problema circolare.
    # Definiamo esplicitamente i percorsi di input e output.
    data_external_dir = PROJECT_ROOT / "data" / "external"
    
    # Il file di input è SEMPRE il database completo scaricato da downloaddata.py.
    input_file = data_external_dir / "scryfall_commons.json"
    
    # Il file di output è SEMPRE la versione semplificata.
    output_file = data_external_dir / "scryfall_commons_simplified.json"
    
    simplify_card_database(input_path=input_file, output_path=output_file)
    
    print("\n--- Processo di Semplificazione Completato ---")
    print(f"Il nuovo file di database si trova in: {output_file}")
    print("\n💡 CONSIGLIO: Assicurati che 'card_db_path' nel tuo file 'config.yaml' punti a questo nuovo file (come hai già fatto).")

if __name__ == "__main__":
    main()