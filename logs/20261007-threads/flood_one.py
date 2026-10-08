import http.client, json, time
END = time.time() + 400
body = json.dumps({"model": "qwen3-embedding:0.6b", "input": ["hammer text"] * 4})
n = 0
conn = http.client.HTTPConnection("127.0.0.1", 11435, timeout=120)
while time.time() < END:
    try:
        conn.request("POST", "/api/embed", body, {"Content-Type": "application/json"})
        r = conn.getresponse(); r.read(); n += 1
        if n % 20 == 0: print("reqs=%d" % n, flush=True)
    except Exception:
        try: conn.close()
        except OSError: pass
        conn = http.client.HTTPConnection("127.0.0.1", 11435, timeout=120)
        time.sleep(0.5)
print("FINAL reqs=%d" % n, flush=True)
