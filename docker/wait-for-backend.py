#!/usr/bin/env python3
import time
import sys
import http.client

host = "backend"
port = 8000
path = "/api/v1/health"  # adjust if needed
max_attempts = 60
interval = 2

for attempt in range(max_attempts):
    try:
        conn = http.client.HTTPConnection(host, port, timeout=2)
        conn.request("GET", path)
        resp = conn.getresponse()
        if resp.status == 200:
            print(f"Backend is up after {attempt+1} attempts.")
            sys.exit(0)
        else:
            print(f"Backend not ready (status {resp.status}), retrying...")
    except Exception as e:
        print(f"Attempt {attempt+1}: Backend not ready ({e}), retrying...")
    time.sleep(interval)
print(f"Backend did not become ready after {max_attempts} attempts.")
sys.exit(1)
