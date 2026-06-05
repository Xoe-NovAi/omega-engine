import yaml
import sys
import os
from pathlib import Path

def validate_soul(file_path):
    try:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        if not data:
            return False, "File is empty"
        
        # Basic structure checks
        required_keys = ['entity']
        for key in required_keys:
            if key not in data:
                return False, f"Missing required key: {key}"
        
        # Check for duplicate lesson IDs
        lessons = data.get('lessons', [])
        ids = [l.get('id') for l in lessons if isinstance(l, dict)]
        if len(ids) != len(set(ids)):
            return False, "Duplicate lesson IDs found"
            
        # Check for duplicate directive IDs
        directives = data.get('directives', [])
        d_ids = [d.get('id') for d in directives if isinstance(d, dict)]
        if len(d_ids) != len(set(d_ids)):
            return False, "Duplicate directive IDs found"

        return True, "Valid"
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_soul.py <path_to_soul_yaml>")
        sys.exit(1)
    
    success, msg = validate_soul(sys.argv[1])
    if success:
        print(f"✅ {sys.argv[1]} is valid")
        sys.exit(0)
    else:
        print(f"❌ {sys.argv[1]} is invalid: {msg}")
        sys.exit(1)
