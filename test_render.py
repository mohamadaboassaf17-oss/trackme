import urllib.request
import urllib.error
import json

FRONTEND = "https://trackme-ugq1.onrender.com"
BACKEND = "https://trackme-backend-xena.onrender.com"

print("=" * 50)
print("Final Test: Frontend + Backend")
print("=" * 50)

# Frontend
print(f"\n[FRONTEND] {FRONTEND}")
try:
    r = urllib.request.urlopen(FRONTEND, timeout=45)
    body = r.read()
    print(f"  Status: {r.status}")
    print(f"  Length: {len(body)}")
    print(f"  Content-Type: {r.headers.get('Content-Type', 'N/A')}")
    is_html = b'<!DOCTYPE' in body or b'<html' in body
    is_vue = b'id="app"' in body
    print(f"  HTML: {'YES' if is_html else 'NO'}")
    print(f"  Vue: {'YES' if is_vue else 'NO'}")
    
    # Check if it references the correct backend
    has_backend = b'trackme-backend-xena' in body
    has_wrong = b'trackme-ugq1' in body and b'api' in body
    print(f"  Backend ref (xena): {'YES' if has_backend else 'NO'}")
    print(f"  Wrong self-ref: {'YES' if has_wrong else 'NO'}")
    
    # Check if JS files are accessible
    import re
    js_files = re.findall(rb'src="([^"]+\.js)"', body)
    css_files = re.findall(rb'href="([^"]+\.css)"', body)
    print(f"  JS files: {len(js_files)}")
    print(f"  CSS files: {len(css_files)}")
    
    if js_files:
        js_url = js_files[0].decode()
        if not js_url.startswith('http'):
            js_url = FRONTEND.rstrip('/') + '/' + js_url.lstrip('/')
        print(f"\n  Testing JS: {js_url[:80]}...")
        try:
            r2 = urllib.request.urlopen(js_url, timeout=30)
            print(f"  JS Status: {r2.status} ({len(r2.read())} bytes)")
        except Exception as e:
            print(f"  JS Error: {e}")
            
except Exception as e:
    print(f"  ERROR: {e}")

# Backend health
print(f"\n[BACKEND] {BACKEND}/api/health")
try:
    r = urllib.request.urlopen(f"{BACKEND}/api/health", timeout=45)
    print(f"  Status: {r.status}")
    print(f"  Body: {r.read().decode()}")
except Exception as e:
    print(f"  ERROR: {e}")

print("\n" + "=" * 50)
