#!/usr/bin/env python3
"""
Download Design2Code and WebSight datasets for benchmarking.
GSCA Protocol: 448×448 image cap, strict categorization, sequential downloads.
"""

import os
import sys
from pathlib import Path
from datasets import load_dataset
from huggingface_hub import login
from PIL import Image
import io

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

DATA_DIR = Path(__file__).parent.parent / "benchmarking"
IMAGES_DIR = DATA_DIR / "images"
DESIGN2CODE_DIR = IMAGES_DIR / "design2code"
WEBSIGHT_DIR = IMAGES_DIR / "websight"

# GSCA Protocol constants
MAX_DIM = 448
DESIGN2CODE_COUNT = 50
WEBSIGHT_COUNT = 40

# Category mappings for GSCA protocol
DESIGN2CODE_CATEGORIES = {
    "login": "auth",
    "signup": "auth",
    "dashboard": "dashboard",
    "landing": "marketing",
    "pricing": "marketing",
    "blog": "content",
    "article": "content",
    "profile": "user",
    "settings": "user",
    "admin": "admin",
    "ecommerce": "ecommerce",
    "checkout": "ecommerce",
    "cart": "ecommerce",
    "product": "ecommerce",
    "form": "form",
    "contact": "form",
    "search": "utility",
    "404": "utility",
    "error": "utility",
}

WEBSIGHT_CATEGORIES = {
    "homepage": "marketing",
    "landing": "marketing",
    "blog": "content",
    "article": "content",
    "documentation": "content",
    "dashboard": "dashboard",
    "admin": "admin",
    "settings": "user",
    "profile": "user",
    "login": "auth",
    "register": "auth",
    "signup": "auth",
    "pricing": "marketing",
    "contact": "form",
    "about": "marketing",
    "services": "marketing",
    "portfolio": "marketing",
    "shop": "ecommerce",
    "product": "ecommerce",
    "cart": "ecommerce",
    "checkout": "ecommerce",
}


def categorize_design2code(example):
    """Categorize Design2Code example per GSCA protocol."""
    # Use the 'category' field if available, otherwise infer from question/type
    cat = example.get("category", "").lower()
    q = example.get("question", "").lower()
    
    for keyword, gsc_cat in DESIGN2CODE_CATEGORIES.items():
        if keyword in cat or keyword in q:
            return gsc_cat
    return "other"


def categorize_websight(example):
    """Categorize WebSight example per GSCA protocol."""
    # Use available metadata fields
    url = example.get("url", "").lower()
    title = example.get("title", "").lower()
    
    for keyword, gsc_cat in WEBSIGHT_CATEGORIES.items():
        if keyword in url or keyword in title:
            return gsc_cat
    return "other"


def resize_image(image_bytes, max_dim=MAX_DIM):
    """Resize image to max dimension while preserving aspect ratio."""
    img = Image.open(io.BytesIO(image_bytes))
    img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
    
    # Convert to RGB if needed (for JPEG)
    if img.mode in ("RGBA", "LA", "P"):
        bg = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        bg.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
        img = bg
    
    output = io.BytesIO()
    img.save(output, format="JPEG", quality=85, optimize=True)
    return output.getvalue()


def download_design2code():
    """Download Design2Code dataset (50 samples)."""
    print(f"Downloading Design2Code ({DESIGN2CODE_COUNT} samples)...")
    DESIGN2CODE_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        # Load dataset - Design2Code is on Hugging Face (SALT-NLP)
        ds = load_dataset("SALT-NLP/Design2Code-hf", split="train", streaming=True)
        
        count = 0
        for example in ds:
            if count >= DESIGN2CODE_COUNT:
                break
            
            # Get image - it's already a PIL Image
            image = example.get("image")
            if image is None:
                continue
            
            # Resize to 448x448 max
            image.thumbnail((MAX_DIM, MAX_DIM), Image.Resampling.LANCZOS)
            
            # Convert to RGB if needed
            if image.mode in ("RGBA", "LA", "P"):
                bg = Image.new("RGB", image.size, (255, 255, 255))
                if image.mode == "P":
                    image = image.convert("RGBA")
                bg.paste(image, mask=image.split()[-1] if image.mode in ("RGBA", "LA") else None)
                image = bg
            
            # Save as JPEG
            output = io.BytesIO()
            image.save(output, format="JPEG", quality=85, optimize=True)
            resized = output.getvalue()
            
            # Categorize from text content
            text = example.get("text", "").lower()
            category = "other"
            for keyword, gsc_cat in DESIGN2CODE_CATEGORIES.items():
                if keyword in text:
                    category = gsc_cat
                    break
            
            # Save with category prefix
            filename = f"design2code_{category}_{count:03d}.jpg"
            filepath = DESIGN2CODE_DIR / filename
            filepath.write_bytes(resized)
            
            print(f"  [{count+1}/{DESIGN2CODE_COUNT}] {filename} ({len(resized)} bytes)")
            count += 1
        
        print(f"✅ Design2Code: {count} images saved to {DESIGN2CODE_DIR}")
        return count
        
    except Exception as e:
        print(f"❌ Design2Code download failed: {e}")
        import traceback
        traceback.print_exc()
        return 0


def download_websight():
    """Download WebSight-Size-10k dataset (40 samples)."""
    print(f"Downloading WebSight ({WEBSIGHT_COUNT} samples)...")
    WEBSIGHT_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        # WebSight dataset
        ds = load_dataset("HuggingFaceM4/WebSight", split="train", streaming=True)
        
        count = 0
        for example in ds:
            if count >= WEBSIGHT_COUNT:
                break
            
            # Get image - check structure
            image = example.get("image")
            if image is None:
                # Try other possible keys
                for key in ["screenshot", "img", "png", "jpg"]:
                    image = example.get(key)
                    if image is not None:
                        break
            if image is None:
                continue
            
            # Handle PIL Image or bytes
            if isinstance(image, Image.Image):
                pil_image = image
            elif hasattr(image, "bytes"):
                pil_image = Image.open(io.BytesIO(image.bytes))
            elif isinstance(image, dict) and "bytes" in image:
                pil_image = Image.open(io.BytesIO(image["bytes"]))
            elif isinstance(image, bytes):
                pil_image = Image.open(io.BytesIO(image))
            else:
                continue
            
            # Resize to 448x448 max
            pil_image.thumbnail((MAX_DIM, MAX_DIM), Image.Resampling.LANCZOS)
            
            # Convert to RGB if needed
            if pil_image.mode in ("RGBA", "LA", "P"):
                bg = Image.new("RGB", pil_image.size, (255, 255, 255))
                if pil_image.mode == "P":
                    pil_image = pil_image.convert("RGBA")
                bg.paste(pil_image, mask=pil_image.split()[-1] if pil_image.mode in ("RGBA", "LA") else None)
                pil_image = bg
            
            # Save as JPEG
            output = io.BytesIO()
            pil_image.save(output, format="JPEG", quality=85, optimize=True)
            resized = output.getvalue()
            
            # Categorize from URL/title
            url = example.get("url", "").lower()
            title = example.get("title", "").lower()
            category = "other"
            for keyword, gsc_cat in WEBSIGHT_CATEGORIES.items():
                if keyword in url or keyword in title:
                    category = gsc_cat
                    break
            
            # Save with category prefix
            filename = f"websight_{category}_{count:03d}.jpg"
            filepath = WEBSIGHT_DIR / filename
            filepath.write_bytes(resized)
            
            print(f"  [{count+1}/{WEBSIGHT_COUNT}] {filename} ({len(resized)} bytes)")
            count += 1
        
        print(f"✅ WebSight: {count} images saved to {WEBSIGHT_DIR}")
        return count
        
    except Exception as e:
        print(f"❌ WebSight download failed: {e}")
        import traceback
        traceback.print_exc()
        return 0


def main():
    """Main download orchestrator."""
    print("=" * 60)
    print("GSCA Dataset Download - Sequential Protocol")
    print("=" * 60)
    print(f"Image cap: {MAX_DIM}×{MAX_DIM}")
    print(f"Design2Code target: {DESIGN2CODE_COUNT}")
    print(f"WebSight target: {WEBSIGHT_COUNT}")
    print(f"Output: {IMAGES_DIR}")
    print()
    
    # Check for HF token
    hf_token = os.environ.get("HF_TOKEN")
    if hf_token:
        login(token=hf_token)
        print("✅ Hugging Face token loaded")
    else:
        print("⚠️  No HF_TOKEN env var - public datasets only")
    
    # Sequential downloads (GSCA protocol)
    d2c_count = download_design2code()
    print()
    ws_count = download_websight()
    print()
    
    print("=" * 60)
    print("DOWNLOAD COMPLETE")
    print(f"Design2Code: {d2c_count}/{DESIGN2CODE_COUNT}")
    print(f"WebSight:    {ws_count}/{WEBSIGHT_COUNT}")
    print(f"Total:       {d2c_count + ws_count}/{DESIGN2CODE_COUNT + WEBSIGHT_COUNT}")
    print("=" * 60)
    
    # Write manifest
    manifest = {
        "design2code": d2c_count,
        "websight": ws_count,
        "max_dim": MAX_DIM,
        "categories_d2c": list(set(DESIGN2CODE_CATEGORIES.values())),
        "categories_ws": list(set(WEBSIGHT_CATEGORIES.values())),
    }
    
    import json
    manifest_path = IMAGES_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"Manifest written to {manifest_path}")
    
    return d2c_count + ws_count


if __name__ == "__main__":
    main()