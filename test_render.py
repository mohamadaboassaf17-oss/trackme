import urllib.request
import urllib.error
import json

BASE = "https://trackme-ugq1.onrender.com"

def test(name, url, method="GET", data=None, timeout=60):
    print(f"\n[{name}] {url}")
    try:
        if method == "POST":
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        else:
            req = urllib.request.Request(url)
        r = urllib.request.urlopen(req, timeout=timeout)
        body = r.read()
        print(f"  Status: {r.status}")
        print(f"  Length: {len(body)}")
        print(f"  Content-Type: {r.headers.get('Content-Type', 'N/A')}")
        print(f"  Body: {body[:300]}")
        return r, body
    except urllib.error.HTTPError as e:
        body = e.read()
        print(f"  Status: {e.code}")
        print(f"  Length: {len(body)}")
        print(f"  Body: {body[:300]}")
        return None, body
    except Exception as e:
        print(f"  ERROR: {e}")
        return None, b""

print("=" * 50)
print("Testing Render Backend")
print("=" * 50)

# Root
test("Root", BASE)

# Health
test("Health", f"{BASE}/api/health")

# OpenAPI JSON  
test("OpenAPI", f"{BASE}/api/openapi.json")

# Docs
test("Swagger", f"{BASE}/api/docs")

# Login  
data = json.dumps({"username": "ahmed", "password": "test1234"}).encode()
r, body = test("Login", f"{BASE}/api/auth/login", method="POST", data=data)

if r and r.status == 200:
    try:
        result = json.loads(body.decode())
        token = result.get("access_token")
        print(f"  Parsed JSON: {list(result.keys()) if result else 'empty'}")
    except Exception as e:
        print(f"  JSON parse error: {e}")
        print(f"  Raw body: {body}")

# Register
data2 = json.dumps({"username": "testuser999", "password": "test9999"}).encode()
test("Register", f"{BASE}/api/auth/register", method="POST", data=data2)

print("\n" + "=" * 50)
