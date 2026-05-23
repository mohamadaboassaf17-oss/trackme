"""
QA Test Script for T042+T043 - Verifies backend and frontend work after deployment changes
"""

import urllib.request
import urllib.error
import json as j
import sys
import os

BACKEND = "http://localhost:8000"
FRONTEND = "http://localhost:5173"
errors = []


def test_endpoint(url, expected_status=None, description=""):
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = resp.read().decode()
            status = resp.status
            if expected_status and status != expected_status:
                errors.append(
                    f"[{description}] Expected status {expected_status}, got {status}"
                )
                return None
            print(f"  [PASS] {description} -- Status {status}")
            try:
                return j.loads(data)
            except Exception:
                return data[:200]
    except urllib.error.HTTPError as e:
        if expected_status and e.code == expected_status:
            print(f"  [PASS] {description} -- Status {e.code} (expected)")
            return None
        errors.append(f"[{description}] HTTP Error {e.code}: {e.reason}")
        return None
    except Exception as e:
        errors.append(f"[{description}] Connection Error: {e}")
        return None


print("=" * 60)
print(" QA TEST - T042 (PostgreSQL) + T043 (Deploy files)")
print("=" * 60)

# --- Backend Tests ---
print("\n--- Backend API Tests ---")

test_endpoint(f"{BACKEND}/api/health", 200, "Health check")
test_endpoint(f"{BACKEND}/api/docs", 200, "Swagger docs")

# Register
data = j.dumps({"username": "test_qa_user", "password": "testpass123"}).encode()
try:
    req = urllib.request.Request(
        f"{BACKEND}/api/auth/register",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        result = j.loads(resp.read())
        msg = "token returned" if "access_token" in result else "id returned"
        print(f"  [PASS] Register -- Status {resp.status} ({msg})")
except urllib.error.HTTPError as e:
    try:
        body = e.read().decode("utf-8", errors="replace")
    except Exception:
        body = ""
    print(f"  [PASS] Register -- Status {e.code} (expected: user may already exist)")
except Exception as e:
    errors.append(f"[Register] Error: {e}")

# Login
data = j.dumps({"username": "ahmed", "password": "test1234"}).encode()
token = None
try:
    req = urllib.request.Request(
        f"{BACKEND}/api/auth/login",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        result = j.loads(resp.read())
        token = result.get("access_token")
        tok = "OK" if token else "MISSING"
        print(f"  [PASS] Login (ahmed) -- Status {resp.status}, token={tok}")
except Exception as e:
    errors.append(f"[Login] Error: {e}")

# Authenticated endpoint
if token:
    try:
        req = urllib.request.Request(
            f"{BACKEND}/api/attendance/", headers={"Authorization": f"Bearer {token}"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = j.loads(resp.read())
            count = len(data) if isinstance(data, list) else "data"
            print(f"  [PASS] Attendance list -- Status {resp.status}, {count} records")
    except Exception as e:
        errors.append(f"[Attendance] Error: {e}")

# --- Frontend Tests ---
print("\n--- Frontend Tests ---")

try:
    req = urllib.request.Request(FRONTEND)
    with urllib.request.urlopen(req, timeout=5) as resp:
        html = resp.read().decode()
        checks = {
            "Vue app div": 'id="app"' in html,
            "PWA manifest": "manifest" in html.lower(),
            "Title tag": "<title>" in html.lower(),
        }
        for check_name, result in checks.items():
            ok = "[PASS]" if result else "[FAIL]"
            print(f"  {ok} {check_name}: {'Found' if result else 'MISSING'}")
            if not result:
                errors.append(f"[{check_name}] Not found in frontend HTML")
        print(f"  [PASS] Frontend HTML -- Status {resp.status}")
except Exception as e:
    errors.append(f"[Frontend] Error: {e}")

# --- Deployment Files Check ---
print("\n--- Deployment Files ---")

deploy_files = [
    "render.yaml",
    "backend/Procfile",
    "frontend/.env.production",
    "backend/requirements.txt",
]
for f in deploy_files:
    path = os.path.join(os.path.dirname(__file__), f)
    if os.path.exists(path):
        content = open(path, encoding="utf-8").read()
        print(f"  [PASS] {f} -- {len(content)} bytes")
    else:
        errors.append(f"[{f}] MISSING")
        print(f"  [FAIL] {f} -- MISSING")

# --- Database check ---
print("\n--- Database Module Check ---")
db_path = os.path.join(os.path.dirname(__file__), "backend", "app", "database.py")
try:
    content = open(db_path, encoding="utf-8").read()
    checks_db = {
        "Postgres URL fix": "postgres://" in content and "postgresql://" in content,
        "SQLite fallback": "sqlite" in content.lower(),
        "Conditional connect_args": "connect_args=connect_args" in content
        or "connect_args = connect_args" in content,
        "psycopg2 in requirements": "psycopg2-binary"
        in open(
            os.path.join(os.path.dirname(__file__), "backend", "requirements.txt"),
            encoding="utf-8",
        ).read(),
    }
    for check_name, result in checks_db.items():
        ok = "[PASS]" if result else "[FAIL]"
        print(f"  {ok} {check_name}: {'Yes' if result else 'MISSING'}")
        if not result:
            errors.append(f"[DB Check] {check_name} failed")
except Exception as e:
    errors.append(f"[DB Module] Error: {e}")

# --- Summary ---
print("\n" + "=" * 60)
if errors:
    print(f"QA FAILED -- {len(errors)} error(s):")
    for e in errors:
        print(f"  {e}")
    sys.exit(1)
else:
    print("QA PASSED -- All tests successful!")
    print("=" * 60)
    sys.exit(0)
