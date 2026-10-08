import os, signal, sys
target = sys.argv[1] if len(sys.argv) > 1 else "flood_fixed.py"
me = os.getpid()
killed = []
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
    if target in c and "python3" in c:
        try:
            os.kill(p, signal.SIGKILL)
            killed.append(p)
        except OSError as e:
            print("fail %d: %s" % (p, e))
print("killed: %s" % killed)
