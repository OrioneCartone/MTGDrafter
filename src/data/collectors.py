import requests
import json
from pathlib import Path
import time

# --- MODIFICA CHIAVE: USARE UN USER-AGENT DA BROWSER ---
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
# --- FINE MODIFICA ---

# La funzione download_scryfall_commons non cambia
def download_scryfall_commons(output_path: Path):
    # ... codice esistente ...
    # (lascia invariata tutta la funzione di Scryfall)
    if output_path.exists():
        print(f"File {output_path.name} già esistente. Salto il download.")
        return
    print("Inizio download di tutte le carte comuni da Scryfall...")
    all_cards = []
    search_url = "https://api.scryfall.com/cards/search?q=r:common"
    while search_url:
        response = None
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(search_url, headers=HEADERS)
                response.raise_for_status()
                print(f"  -> Pagina scaricata con successo (tentativo {attempt + 1})")
                break 
            except requests.RequestException as e:
                print(f"ERRORE: Tentativo {attempt + 1}/{max_retries} fallito. Errore: {e}")
                if attempt + 1 == max_retries:
                    print("Massimo numero di tentativi raggiunto. Interruzione dello script.")
                    return
                wait_time = 5 * (attempt + 1)
                print(f"Attendo {wait_time} secondi prima di riprovare...")
                time.sleep(wait_time)
        if not response:
             return
        data = response.json()
        all_cards.extend(data['data'])
        if data['has_more']:
            search_url = data['next_page']
            print(f"  -> Trovata un'altra pagina... (totale carte: {len(all_cards)})")
        else:
            search_url = None
        time.sleep(0.1)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_cards, f, indent=2)
    print(f"✅ Download completato. {len(all_cards)} carte comuni salvate in {output_path}")


def download_cubecobra_list(cube_id: str, output_path: Path):
    # Questa funzione rimane identica a quella che ti ho dato prima
    # con i controlli, ma ora userà i NUOVI HEADERS definiti sopra.
    if output_path.exists():
        print(f"Cubo '{cube_id}' già esistente. Salto il download.")
        return
        
    url = f"https://cubecobra.com/cube/api/cubelist/{cube_id}"
    print(f"Inizio download del cubo '{cube_id}' da {url}...")
    try:
        response = requests.get(url, headers=HEADERS) # Userà il nuovo header
        response.raise_for_status()
        if response.text.strip().startswith('<'):
            print(f"ERRORE: CubeCobra ha restituito una pagina HTML invece di una lista di carte per '{cube_id}'. Salto.")
            return
        card_names = response.text.strip().split('\n')
        if len(card_names) < 100:
            print(f"ERRORE: Trovate solo {len(card_names)} carte per il cubo '{cube_id}'. Potrebbe essere un errore. Salto il salvataggio.")
            print("Contenuto ricevuto:", response.text[:200])
            return
        cube_data = { "id": cube_id, "card_count": len(card_names), "cards": card_names }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(cube_data, f, indent=2)
        print(f"✅ Cubo '{cube_id}' ({len(card_names)} carte) salvato in {output_path}")
    except requests.RequestException as e:
        print(f"ERRORE: Download del cubo '{cube_id}' fallito. {e}")


