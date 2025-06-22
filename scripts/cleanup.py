import shutil
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

# Definiamo le cartelle specifiche per il nostro esperimento "Pauper Generalist"
LOGS_DIR = PROJECT_ROOT / "data" / "processed" / "pauper_generalist_logs"
MODELS_DIR = PROJECT_ROOT / "models" / "experiments" / "transformer_v1"

def clean_directory(dir_path: Path):
    """
    Cancella tutto il contenuto di una directory, ma non la directory stessa.
    Se la directory non esiste, la crea.
    """
    if dir_path.exists():
        print(f"Pulizia della directory: {dir_path}...")
        shutil.rmtree(dir_path)
    else:
        print(f"La directory {dir_path} non esiste, nulla da pulire.")
    
    dir_path.mkdir(parents=True, exist_ok=True)
    print(f"Directory {dir_path} vuota e pronta.")

def main():
    """Script principale per pulire gli artefatti generati dall'esperimento generalista."""
    print("--- Avvio Pulizia Artefatti (Pauper Generalist) ---")
    
    dirs_to_clean = [
        LOGS_DIR,
        MODELS_DIR
    ]
    
    for directory in dirs_to_clean:
        clean_directory(directory)
        
    print("\n✅ Pulizia completata. Pronto per un nuovo ciclo.")

if __name__ == "__main__":
    main()
