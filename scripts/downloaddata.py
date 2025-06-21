# ... (import e PROJECT_ROOT) ...
from src.data.collectors import download_scryfall_commons, download_cubecobra_list
# ...

def main():
    """Script per scaricare i dati necessari per l'ambiente Pauper Cube."""
    print("--- Avvio download dati (Focus: Pauper) ---")

    # 1. Scarica il database di TUTTE le carte comuni. È il nostro dizionario.
    download_scryfall_commons(output_path=SCRYFALL_OUTPUT_FILE)

    # 2. Scarica le liste dei cubi di sole comuni che useremo come benchmark.
    # Ci concentriamo su "thepaupercube" come principale.
    pauper_cubes_to_download = [
        "thepaupercube",            # Il nostro cubo di riferimento primario
        "downshifted",              # Un altro Pauper Cube popolare per varietà
        # "pauper_cube_with_downshifts" # Un altro esempio se vuoi più dati
    ]
    
    print("\n--- Download Liste Cubi Pauper ---")
    for cube_id in pauper_cubes_to_download:
        cube_output_path = CUBE_LISTS_DIR / f"{cube_id}.json"
        download_cubecobra_list(cube_id=cube_id, output_path=cube_output_path)

    print("\n--- Download completato. ---")

# ... (il resto dello script) ...
