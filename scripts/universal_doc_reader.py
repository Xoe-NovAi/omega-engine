#!/usr/bin/env python3
"""Universal document reader for agents - handles .docx, .pdf, .odt, .rtf, .html, .md, .txt"""
import sys
import os

def read_docx(path):
    try:
        import docx
        doc = docx.Document(path)
        return '\n'.join([p.text for p in doc.paragraphs])
    except Exception as e:
        return f"[DOCX ERROR: {e}]"

def read_pdf(path):
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(path)
        return '\n'.join([page.get_text() for page in doc])
    except Exception as e:
        return f"[PDF ERROR: {e}]"

def read_odt(path):
    try:
        from odf import text, teletype
        from odf.opendocument import load
        doc = load(path)
        return '\n'.join([teletype.extractText(p) for p in doc.getElementsByType(text.P)])
    except Exception as e:
        return f"[ODT ERROR: {e}]"

def read_rtf(path):
    try:
        from striprtf.striprtf import rtf_to_text
        with open(path, 'r') as f:
            return rtf_to_text(f.read())
    except Exception as e:
        return f"[RTF ERROR: {e}]"

def read_html(path):
    try:
        from bs4 import BeautifulSoup
        with open(path, 'r') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            return soup.get_text()
    except Exception as e:
        return f"[HTML ERROR: {e}]"

def read_text(path):
    try:
        with open(path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"[TEXT ERROR: {e}]"

def main():
    if len(sys.argv) < 2:
        print("Usage: universal_doc_reader.py <file_path>")
        sys.exit(1)
    
    path = sys.argv[1]
    ext = os.path.splitext(path)[1].lower()
    
    readers = {
        '.docx': read_docx,
        '.pdf': read_pdf,
        '.odt': read_odt,
        '.rtf': read_rtf,
        '.html': read_html,
        '.htm': read_html,
        '.md': read_text,
        '.txt': read_text,
        '.json': read_text,
        '.yaml': read_text,
        '.yml': read_text,
    }
    
    reader = readers.get(ext, read_text)
    print(reader(path))

if __name__ == '__main__':
    main()
