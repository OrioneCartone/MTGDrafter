from pathlib import Path
import sys

# Aggiunge la root del progetto al path per importare da 'src'
# Questo rende lo script eseguibile da qualsiasi posizione
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

# Importiamo direttamente le funzioni, non le classi
from src.data.collectors import download_scryfall_commons, download_cubecobra_list

# Definiamo i percorsi di output qui, in modo chiaro
DATA_DIR = PROJECT_ROOT / "data"
SCRYFALL_OUTPUT_FILE = DATA_DIR / "external" / "scryfall_commons.json"
CUBE_LISTS_DIR = DATA_DIR / "raw" / "cube_lists"

def main():
    """Script principale per scaricare i dati necessari."""
    print("--- Avvio download dati ---")

    # 1. Scarica il database delle carte comuni
    download_scryfall_commons(output_path=SCRYFALL_OUTPUT_FILE)

    # 2. Scarica le liste dei cubi
    # Potremmo voler scaricare solo cubi di comuni, come "thepaupercube"
    cubes_to_download = [
        "thepaupercube",
        "pauper_cube_with_downshifts",
        # "vintage_cube_2023" # Questo contiene rare, potremmo non volerlo ora
    ]
    
    print("\n--- Download liste cubi ---")
    for cube_id in cubes_to_download:
        cube_output_path = CUBE_LISTS_DIR / f"{cube_id}.json"
        download_cubecobra_list(cube_id=cube_id, output_path=cube_output_path)

    print("\n--- Download completato. ---")

if __name__ == "__main__":
    main()
