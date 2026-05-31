"""Ancient Greek Support — Greek-BERT and Krikri integration for the library system.

AP: AP-OMEGA-GREEK-v1.0.0
ICS: [NODE: THOTH | ARCHETYPE: OSIRIS | MODEL: KRIKRI-7B-INSTRUCT | CONTEXT: ANCIENT-GREEK]

Provides:
  - Ancient Greek text detection (polytonic Greek Unicode ranges)
  - Greek text normalization (strip accents, normalize Unicode)
  - Greek-BERT embedding integration (when available)
  - Krikri-7B-Instruct model spec for Greek-capable inference
  - Domain classification for classics/esoteric/philosophy texts

Integrates with:
  - ContentExtractor for Greek text detection
  - Indexer for Greek-aware tokenization
  - CurationPipeline for classics domain classification
  - ResearchEngine for Greek text synthesis

Model specs:
  - Ancient-Greek-BERT: Ancient Greek NLP, embeddings, lemmatization
  - Krikri-7B-Instruct: Modern + Ancient Greek instruction-following (GGUF)
"""

import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Unicode ranges for Ancient Greek (polytonic)
GREEK_RANGES = [
    (0x0370, 0x03FF),  # Greek and Coptic
    (0x1F00, 0x1FFF),  # Greek Extended (polytonic)
    (0x10140, 0x1018F),  # Ancient Greek Numbers
    (0x1D200, 0x1D24F),  # Ancient Greek Musical Notation
]

# Common ancient Greek words for detection
ANCIENT_GREEK_INDICATORS = {
    "φιλοσοφία", "ψυχή", "λόγος", "νοῦς", "ἀλήθεια", "δικαιοσύνη",
    "ἀρετή", "καλός", "ἀγαθός", "δύναμις", "ἐνέργεια", "οὐσία",
    "ἰδέα", "μορφή", "αἰτία", "τέλος", "ἀρχή", "κόσμος",
    "φύσις", "θεός", "ἄνθρωπος", "πολιτεία", "ἐπιστήμη",
    "ἡδονή", "λύπη", "πάθος", "ἔρως", "θάνατος", "ζωή",
    "Ἑρμῆς", "Τρισμέγιστος", "γνῶσις", "σοφία", "μαγεία",
    "ἀστρολογία", "ἀλχημεία", "θεουργία", "ἱερατική",
    "Πυθαγόρας", "Πλάτων", "Ἀριστοτέλης", "Σωκράτης",
    "Πλωτῖνος", "Πορφύριος", "Ἰάμβλιχος", "Πρόκλος",
}

CLASSICS_KEYWORDS = {
    "plato", "aristotle", "socrates", "pythagoras", "plotinus",
    "porphyry", "iamblichus", "proclus", "plutarch", "epictetus",
    "stoic", "epicurean", "neoplatonism", "hermetic", "gnostic",
    "corpus hermeticum", "orphic", "eleusinian", "dionysian",
    "apollonian", "socratic", "platonic", "aristotelian",
}

ESOTERIC_KEYWORDS = {
    "hermetic", "alchemy", "astrology", "theurgy", "gnosis",
    "kabbalah", "tarot", "occult", "esoteric", "mystical",
    "rosicrucian", "illuminati", "mason", "theosophy",
    "anthroposophy", "spiritual", "alchemical", "magical",
    "divination", "oracle", "initiation", "mystery school",
}

PSYCHOLOGY_KEYWORDS = {
    "psyche", "consciousness", "unconscious", "archetype",
    "jung", "freud", "shadow", "anima", "animus", "individuation",
    "persona", "ego", "collective unconscious", "synchronicity",
    "dream", "symbol", "myth", "narrative", "trauma",
    "developmental", "cognitive", "behavioral", "phenomenological",
}

_bert_available = None


def is_greek_text(text: str, threshold: float = 0.1) -> bool:
    """Check if text contains a significant amount of Greek characters.

    Args:
        text: Text to check
        threshold: Minimum fraction of Greek chars to classify as Greek (default 0.1)

    Returns:
        True if the text is significantly Greek
    """
    if not text:
        return False
    greek_chars = 0
    total_chars = max(len(text), 1)
    for char in text:
        cp = ord(char)
        for start, end in GREEK_RANGES:
            if start <= cp <= end:
                greek_chars += 1
                break
    return (greek_chars / total_chars) >= threshold


def normalize_greek(text: str) -> str:
    """Normalize Ancient Greek text: strip accents, normalize Unicode.

    Removes polytonic accents, breathing marks, and iota subscripts
    for search/comparison purposes.

    Args:
        text: Greek text to normalize

    Returns:
        Normalized text (monotonic)
    """
    if not text:
        return text

    import unicodedata

    # Normalize Unicode decomposition
    text = unicodedata.normalize("NFD", text)

    # Remove combining diacritical marks
    # Combining characters: grave, acute, circumflex, macron, breve,
    # diaeresis, rough breathing, smooth breathing, iota subscript
    combining_pattern = re.compile(
        r"[\u0300-\u036F\u0340-\u034F\u0483-\u0489\u0591-\u05BD\u05BF\u05C1\u05C2\u05C4\u05C5\u05C7]"
    )
    text = combining_pattern.sub("", text)

    return unicodedata.normalize("NFC", text)


def detect_ancient_greek_indicators(text: str) -> List[str]:
    """Detect Ancient Greek philosophical/esoteric terms in text.

    Args:
        text: Text to scan

    Returns:
        List of detected Greek terms (transliterated)
    """
    detected = []
    text_lower = text.lower()
    for term in ANCIENT_GREEK_INDICATORS:
        if term in text_lower:
            detected.append(term)
    return detected


def classify_classics_domain(text: str) -> str:
    """Classify text into classics/esoteric/psychology/science domains.

    Returns one of: "classics", "esoteric", "psychology", "science", "general"
    """
    text_lower = text.lower()
    scores: Dict[str, int] = {"classics": 0, "esoteric": 0, "psychology": 0, "science": 0}

    for keyword in CLASSICS_KEYWORDS:
        if keyword in text_lower:
            scores["classics"] += 1

    for keyword in ESOTERIC_KEYWORDS:
        if keyword in text_lower:
            scores["esoteric"] += 1

    for keyword in PSYCHOLOGY_KEYWORDS:
        if keyword in text_lower:
            scores["psychology"] += 1

    # Greek text presence heavily biases toward classics/esoteric
    if is_greek_text(text):
        scores["classics"] += 3
        scores["esoteric"] += 1

    # Detect Greek terms
    indicators = detect_ancient_greek_indicators(text)
    if indicators:
        scores["classics"] += len(indicators)
        # Some Greek terms also indicate esoteric/philosophical
        esoteric_terms = {"γνῶσις", "μαγεία", "θεουργία", "ἀστρολογία", "ἀλχημεία"}
        for t in indicators:
            if t in esoteric_terms:
                scores["esoteric"] += 2

    max_score = max(scores.values())
    if max_score == 0:
        return "general"

    # Return highest scoring domain
    max_domains = [d for d, s in scores.items() if s == max_score]
    return max_domains[0]


def get_krikri_model_spec() -> Dict:
    """Get model spec for Krikri-8b-Instruct (Greek-capable)."""
    return {
        "name": "krikri-8b-instruct",
        "description": "Krikri-8b-Instruct — Greek-capable instruction model (Modern + Ancient Greek)",
        "path": "/media/arcana-novai/omega_library/models/gguf/Krikri-8b-Instruct-Q5_K_M.gguf",
        "alternative_paths": [],
        "languages": ["el", "grc", "en"],
        "capabilities": ["greek_text", "ancient_greek", "instruction_following", "translation"],
        "context_window": 16384,
        "temperature": 0.7,
    }


def get_greek_bert_spec() -> Dict:
    """Get model spec for Ancient-Greek-BERT."""
    return {
        "name": "ancient-greek-bert",
        "description": "Ancient-Greek-BERT — BERT model for Ancient Greek NLP",
        "type": "sentence_transformer",
        "expected_path": os.path.expanduser("~/omega/models/ancient-greek-bert"),
        "alternatives": [
            "bow (bag-of-words fallback — built into indexer)",
        ],
        "capabilities": [
            "ancient_greek_embeddings",
            "greek_text_classification",
            "greek_lemmatization",
            "semantic_search_greek",
        ],
        "fallback": "The Indexer uses lightweight bag-of-words embeddings for Greek text when BERT is unavailable",
    }


def is_bert_available() -> bool:
    """Check if Ancient-Greek-BERT or any sentence-transformer is available."""
    global _bert_available
    if _bert_available is not None:
        return _bert_available
    try:
        import sentence_transformers
        _bert_available = True
        logger.info("sentence-transformers available for Greek embeddings")
    except ImportError:
        _bert_available = False
        logger.info("sentence-transformers not installed; using fallback embeddings for Greek text")
    return _bert_available
