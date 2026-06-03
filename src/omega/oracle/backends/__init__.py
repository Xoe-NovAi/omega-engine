# 🔱 Omega Backends — Provider Implementation Registry
# [id-soft: q3a-1999] 4-Path VFS — provider chain is a search path
#   Q3A's files.c defines a search path that falls through multiple
#   directories. The backends package is the same: mock → local → cloud,
#   each tried in order until one succeeds.