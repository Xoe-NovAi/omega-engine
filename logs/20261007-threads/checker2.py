import os
me = os.getpid()
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
    if "flood_one.py" in c or ("llama-server" in c):
        print(p, c[:150])
