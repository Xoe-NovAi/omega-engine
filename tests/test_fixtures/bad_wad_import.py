# Test fixture: Contains WAD-specific imports/references for firewall testing
# This file SHOULD trigger firewall violations

from config.wads.arcana_novai import entities  # Forbidden: config.wads import
import config.wads.doom_universe  # Forbidden: config.wads import

# Forbidden WAD entity references
SEKHMET = "Sekhmet"
BRIGID = "Brigid"
PROMETHEUS = "Prometheus"
SARASWATI = "Saraswati"
INANNA = "Inanna"
ERESHKIGAL = "Ereshkigal"
LUCIFER = "Lucifer"
HECATE = "Hecate"
ANUBIS = "Anubis"
KALI = "Kali"

# Forbidden WAD identifiers
WAD_ID = "arcana_novai"
WAD_ID_2 = "doom_universe"
WAD_ID_3 = "torment_stack"