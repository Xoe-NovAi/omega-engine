import os
import shutil
from pathlib import Path

SOURCE_DIR = Path("/home/arcana-novai/Documents/Xoe-NovAi/omega-stack-legacy/infra/docker/models")
TARGET_DIR = Path("/media/arcana-novai/omega_library/models/gguf/local/all")

def merge_models():
    if not SOURCE_DIR.exists():
        print(f"Source directory {SOURCE_DIR} does not exist.")
        return

    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    
    models = list(SOURCE_DIR.glob("*.gguf"))
    print(f"Found {len(models)} models in legacy directory.")

    for model_path in models:
        model_name = model_path.name
        target_path = TARGET_DIR / model_name
        
        if target_path.exists():
            print(f"Model {model_name} already exists in target. Deleting legacy copy.")
            model_path.unlink()
        else:
            print(f"Migrating {model_name} to LM Studio local/all directory...")
            shutil.move(str(model_path), str(target_path))

if __name__ == "__main__":
    merge_models()
