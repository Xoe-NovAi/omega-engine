import ast
import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("somatic-validator")

def find_doc_refs(file_path: Path):
    """Parses a python file for 'DocRef: path/to/doc.md' tags in docstrings."""
    refs = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                docstring = ast.get_docstring(node)
                if docstring:
                    # Look for 'DocRef: path/to/doc.md'
                    if "DocRef:" in docstring:
                        # Extract the path after 'DocRef:'
                        parts = docstring.split("DocRef:")
                        # We take the first line after the tag
                        ref_line = parts[1].split("\n")[0].strip()
                        refs.append((node.name, ref_line))
    except Exception as e:
        logger.error(f"Failed to parse {file_path}: {e}")
    
    return refs

def validate_links(root_dir: Path):
    """Walks the src directory and validates all DocRef tags."""
    all_refs = []
    for py_file in root_dir.rglob("*.py"):
        all_refs.extend([
            (py_file, name, ref) for name, ref in find_doc_refs(py_file)
        ])
    
    errors = 0
    for py_file, name, ref in all_refs:
        # Resolve the ref path relative to the project root
        # The ref is expected to be relative to the project root (e.g., 'docs/reference/api/oracle.md')
        ref_path = root_dir.parents[1] / ref # root_dir is src/omega, parents[1] is project root
        
        if not ref_path.exists():
            logger.error(f"Broken DocRef in {py_file}:{name} -> {ref} (File not found)")
            errors += 1
        else:
            logger.info(f"Valid DocRef: {py_file}:{name} -> {ref}")
            
    return errors

if __name__ == "__main__":
    # Project root is the parent of 'src'
    project_root = Path(__file__).resolve().parent.parent
    src_dir = project_root / "src" / "omega"
    
    logger.info(f"Validating Somatic-Doc links in {src_dir}...")
    error_count = validate_links(src_dir)
    
    if error_count > 0:
        logger.error(f"Somatic-Doc validation failed: {error_count} broken links found.")
        exit(1)
    else:
        logger.info("Somatic-Doc validation passed! All links are healthy.")
        exit(0)
