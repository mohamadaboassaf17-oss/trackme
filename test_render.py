import urllib.request

print("Checking what root / returns:")
try:
    r = urllib.request.urlopen("https://trackme-ugq1.onrender.com/", timeout=45)
    body = r.read()
    print(f"Status: {r.status}")
    print(f"Length: {len(body)}")
    print(f"First 200 chars: {body[:200]}")
    print()
    # Check if it's HTML or JSON
    if body.startswith(b"<!DOCTYPE") or body.startswith(b"<html"):
        print(">>> ROOT IS SERVING THE VUE FRONTEND (StaticFiles mount active)")
        print(">>> This means the old code is running - needs redeploy!")
    elif body.startswith(b"{"):
        print(">>> ROOT IS SERVING JSON (API is working)")
    else:
        print(">>> UNKNOWN RESPONSE TYPE")
        
except Exception as e:
    print(f"ERROR: {e}")

print("\n--- Testing with sleep (Render cold start) ---")
import time
print("Waiting 30s for Render to wake up...")
time.sleep(30)

try:
    r = urllib.request.urlopen("https://trackme-ugq1.onrender.com/api/health", timeout=45)
    print(f"Status: {r.status}")
    print(f"Body: {r.read().decode()}")
except Exception as e:
    print(f"ERROR: {e}")
