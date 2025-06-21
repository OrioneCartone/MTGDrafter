import requests
import json
from pathlib import Path
import time

HEADERS = {"User-Agent": "MTGCubeAI-Project-Script"}

def download_scryfall_commons(output_path: Path):
    """
    Usa l'API di ricerca di Scryfall per scaricare tutte le carte comuni.
    Implementa un meccanismo di retry per gestire errori temporanei del server.
    """
    if output_path.exists():
        print(f"File {output_path.name} già esistente. Salto il download.")
        return

    print("Inizio download di tutte le carte comuni da Scryfall...")
    
    all_cards = []
    search_url = "https://api.scryfall.com/cards/search?q=r:common"

    while search_url:
        response = None # Inizializziamo a None per il ciclo di retry
        
        # --- Blocco di tentativi (Retry) ---
        # Tenta la richiesta fino a 3 volte prima di arrendersi
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Effettua la richiesta
                response = requests.get(search_url, headers=HEADERS)
                # Se il server risponde con un errore (es. 503), lancia un'eccezione
                response.raise_for_status() 
                # Se la richiesta ha successo, esci dal ciclo di retry
                print(f"  -> Pagina scaricata con successo (tentativo {attempt + 1})")
                break 
            except requests.RequestException as e:
                print(f"ERRORE: Tentativo {attempt + 1}/{max_retries} fallito. Errore: {e}")
                if attempt + 1 == max_retries:
                    print("Massimo numero di tentativi raggiunto. Interruzione dello script.")
                    return # Arrenditi e esci dalla funzione
                
                # Attendi prima di riprovare
                wait_time = 5 * (attempt + 1) # Attesa crescente (5s, 10s, 15s)
                print(f"Attendo {wait_time} secondi prima di riprovare...")
                time.sleep(wait_time)
        # --- Fine del blocco di tentativi ---

        # Se siamo qui e response è ancora None, significa che tutti i tentativi sono falliti
        if not response:
             return # Uscita di sicurezza

        data = response.json()
        all_cards.extend(data['data'])

        if data['has_more']:
            search_url = data['next_page']
            print(f"  -> Trovata un'altra pagina... (totale carte: {len(all_cards)})")
        else:
            search_url = None

        # Manteniamo la piccola pausa "educata" tra una pagina e l'altra
        time.sleep(0.1)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_cards, f, indent=2)

    print(f"✅ Download completato. {len(all_cards)} carte comuni salvate in {output_path}")


# La funzione per CubeCobra può rimanere invariata, è meno soggetta a questi problemi
def download_cubecobra_list(cube_id: str, output_path: Path):
    """
    Scarica una lista di carte da CubeCobra e la salva in formato JSON.
    """
    if output_path.exists():
        print(f"Cubo '{cube_id}' già esistente. Salto il download.")
        return
        
    url = f"https://cubecobra.com/api/cubelist/{cube_id}"
    print(f"Inizio download del cubo '{cube_id}'...")

    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        card_names = response.text.strip().split('\n')
        cube_data = {
            "id": cube_id,
            "card_count": len(card_names),
            "cards": card_names
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(cube_data, f, indent=2)
        print(f"✅ Cubo '{cube_id}' salvato in {output_path}")
    except requests.RequestException as e:
        print(f"ERRORE: Download del cubo '{cube_id}' fallito. {e}")

