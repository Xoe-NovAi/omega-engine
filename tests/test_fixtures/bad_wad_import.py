# Test fixture: Contains WAD-specific imports/references for firewall testing
# This file SHOULD trigger firewall violations

from config.wads.forbidden_wad import entities  # Forbidden: config.wads import
import config.wads.another_forbidden_wad  # Forbidden: config.wads import

# Forbidden WAD entity references (NOT in CORE_ENGINE_PATTERNS)
BRIGID = "Brigid"
SARASWATI = "Saraswati"
INANNA = "Inanna"
ERESHKIGAL = "Ereshkigal"
LUCIFER = "Lucifer"
HECATE = "Hecate"
ANUBIS = "Anubis"

# Forbidden WAD identifiers (NOT in CORE_ENGINE_PATTERNS)
WAD_ID = "forbidden_wad_name"
WAD_ID_2 = "another_forbidden_wad"