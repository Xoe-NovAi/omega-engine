import os
me = os.getpid()
found = []
for pid in os.listdir("/proc"):
    if not pid.isdigit():
        continue
    p = int(pid)
    if p == me:
        continue
    try:
        c = open("/proc/%d/cmdline" % p, "rb").read().decode().replace("\0", " ")
    except OSError:
        continue
    if "flood_fixed.py" in c:
        found.append((p, c[:120]))
print("remaining flood workers: %s" % found)
found2 = []
for pid in os.listdir("/proc"):
    if not pid.isdigit():
        continue
    p = int(pid)
    try:
        c = open("/proc/%d/cmdline" % p, "rb").read().decode().replace("\0", " ")
    except OSError:
        continue
    if "llama-server" in c and "embedding" in c:
        found2.append(p)
print("embed runners: %s" % found2)
