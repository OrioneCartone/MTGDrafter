import yaml
from pathlib import Path

def load_config() -> dict:
    """Carica il file di configurazione principale (config.yaml)."""
    project_root = Path(__file__).parent.parent.parent
    config_path = project_root / "config" / "config.yaml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"File di configurazione non trovato in: {config_path}")
        
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
        
    return config

# Carica la configurazione una sola volta quando il modulo viene importato.
# Altri file possono semplicemente importare questa variabile CONFIG.
CONFIG = load_config()