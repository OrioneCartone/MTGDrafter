from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))


from src.data.collectors import download_scryfall_commons, download_cubecobra_list

# --- Configurazione ---
DATA_DIR = PROJECT_ROOT / "data"
SCRYFALL_OUTPUT_FILE = DATA_DIR / "external" / "scryfall_commons.json"
CUBE_LISTS_DIR = DATA_DIR / "raw" / "cube_lists"

def main():
    """Script per scaricare i dati necessari per l'ambiente Pauper."""
    print("--- Avvio download dati (Focus: Pauper) ---")

    download_scryfall_commons(output_path=SCRYFALL_OUTPUT_FILE)

    pauper_cubes_to_download = [
        "thepaupercube",
        "mengupaupercube",
        "difinitivepauper",
        "gilpauper",
        "4cd0h"
    ]
    
    print("\n--- Download Liste Cubi Pauper ---")
    for cube_id in pauper_cubes_to_download:
        cube_output_path = CUBE_LISTS_DIR / f"{cube_id}.json"
        download_cubecobra_list(cube_id=cube_id, output_path=cube_output_path)

    print("\n--- Download completato. ---")

if __name__ == "__main__":
    main()
