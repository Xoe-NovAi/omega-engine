import http.client, json, time, sys
END = time.time() + int(sys.argv[1] if len(sys.argv) > 1 else 120)
body = json.dumps({"model": "qwen3-embedding:0.6b", "input": ["The quick brown fox jumps over the lazy dog. " * 8] * 16})
n = 0; errs = 0
conn = http.client.HTTPConnection("127.0.0.1", 11435, timeout=120)
while time.time() < END:
    try:
        conn.request("POST", "/api/embed", body, {"Content-Type": "application/json"})
        r = conn.getresponse(); r.read()
        n += 1
        if n % 10 == 0: print(f"reqs={n} errs={errs}", flush=True)
    except Exception as e:
        errs += 1
        try: conn.close()
        except OSError: pass
        conn = http.client.HTTPConnection("127.0.0.1", 11435, timeout=120)
        time.sleep(0.5)
print(f"FINAL reqs={n} errs={errs}", flush=True)
