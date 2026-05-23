import urllib.request

try:
    r = urllib.request.urlopen("https://trackme-ugq1.onrender.com/", timeout=30)
    body = r.read()
    print("Status:", r.status)
    print("Length:", len(body))
    print("Contains html:", b"<!DOCTYPE" in body or b"<!doctype" in body)
    print("Contains vue:", b'id="app"' in body or b"Vue" in body)
    print("First 100 bytes (repr):", repr(body[:100]))
except Exception as e:
    print("Error:", e)

print("\n--- Testing /api/health ---")
try:
    r = urllib.request.urlopen("https://trackme-ugq1.onrender.com/api/health", timeout=30)
    print("Status:", r.status)
    print("Body:", r.read().decode())
except Exception as e:
    print("Error:", e)

print("\n--- Testing /api/docs ---")
try:
    r = urllib.request.urlopen("https://trackme-ugq1.onrender.com/api/docs", timeout=30)
    print("Status:", r.status)
except Exception as e:
    print("Error:", e)
