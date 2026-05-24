from playwright.sync_api import sync_playwright
import json, os, time, random, string

FRONTEND = "https://trackme-ugq1.onrender.com"
BACKEND = "https://trackme-backend-xena.onrender.com"
OUTPUT = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(OUTPUT, exist_ok=True)

def random_user():
    ts = str(int(time.time() * 1000))[-6:]
    return f"test_{ts}"

def screenshot(page, name):
    path = os.path.join(OUTPUT, f"live_{name}.png")
    page.screenshot(path=path, full_page=True)
    print(f"  Screenshot: {name}")
    return path

def check_console(page):
    errors = [msg for msg in page.console_logs if msg.type == "error" or "Uncaught" in msg.text]
    if errors:
        print(f"  WARNING: Console errors ({len(errors)}):")
        for e in errors[:3]:
            print(f"      {e.text[:100]}")
    return errors

def run_test():
    results = {"passed": 0, "failed": 0}
    def check(name, condition, detail=""):
        if condition:
            print(f"  PASS: {name}")
            results["passed"] += 1
        else:
            print(f"  FAIL: {name} - {detail}")
            results["failed"] += 1

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.console_logs = []
        page.on("console", lambda msg: page.console_logs.append(msg))

        USER = random_user()
        PASS = "Test1234!"

        # ===== 1. Check backend health =====
        print("\n[1] Backend Health Check")
        resp = page.request.get(f"{BACKEND}/health")
        check("Health endpoint", resp.ok)
        if resp.ok:
            data = resp.json()
            check("Health returns ok", data.get("status") == "ok")

        # ===== 2. Check security headers =====
        print("\n[2] Security Headers")
        headers = resp.headers
        check("X-Frame-Options: DENY", headers.get("x-frame-options") == "DENY")
        check("X-Content-Type-Options: nosniff", headers.get("x-content-type-options") == "nosniff")
        check("X-XSS-Protection present", headers.get("x-xss-protection") is not None)

        # ===== 3. Open frontend =====
        print("\n[3] Frontend Load Test")
        page.goto(FRONTEND, wait_until="networkidle", timeout=60000)
        time.sleep(3)
        screenshot(page, "01_frontend_load")
        input_count = page.locator("input").count()
        check("Frontend loads with inputs", input_count > 0, f"inputs={input_count}, title={page.title()}")
        check("No console errors on load", len(check_console(page)) == 0)

        # ===== 4. Registration via API =====
        print("\n[4] Registration Test")
        import json as _json
        resp = page.request.post(f"{BACKEND}/api/auth/register", data=_json.dumps({
            "username": USER,
            "email": f"{USER}@test.com",
            "password": PASS
        }), headers={"Content-Type": "application/json"})
        check("Register API works", resp.ok, f"status={resp.status}")
        if resp.ok:
            reg_data = resp.json()
            check("Register returns user data", "username" in reg_data or "id" in reg_data)

        # ===== 5. Login flow =====
        print("\n[5] Login Flow")
        page.goto(f"{FRONTEND}/login", wait_until="networkidle", timeout=60000)
        time.sleep(2)
        screenshot(page, "02_login_page")

        inputs = page.locator("input").all()
        print(f"  Found {len(inputs)} inputs")
        for inp in inputs:
            placeholder = inp.get_attribute("placeholder") or ""
            if "اسم" in placeholder or "مستخدم" in placeholder or "user" in placeholder.lower():
                inp.fill(USER)
                print(f"  Filled username")
            elif "كلمة" in placeholder or "مرور" in placeholder or "password" in placeholder.lower():
                inp.fill(PASS)
                print(f"  Filled password")

        buttons = page.locator("button").all()
        for btn in buttons:
            text = btn.inner_text()
            if "دخول" in text or "login" in text.lower():
                btn.click()
                print(f"  Clicked login button")
                break

        time.sleep(5)
        page.wait_for_load_state("networkidle")
        screenshot(page, "03_after_login")

        current_url = page.url
        check("Redirected after login", "/dashboard" in current_url, f"url={current_url}")
        check("No console errors on login", len(check_console(page)) == 0)

        # ===== 6. Dashboard =====
        print("\n[6] Dashboard Page")
        page.goto(f"{FRONTEND}/dashboard", wait_until="networkidle", timeout=60000)
        time.sleep(3)
        screenshot(page, "04_dashboard")
        check("Dashboard loads", page.locator("body").is_visible())
        card_count = page.locator(".card, .kpi-card, [class*='kpi'], [class*='stat'], [class*='summary']").count()
        print(f"  Cards/Stats found: {card_count}")
        check("No console errors on dashboard", len(check_console(page)) == 0)

        # ===== 7. Attendance page =====
        print("\n[7] Attendance Page")
        page.goto(f"{FRONTEND}/attendance", wait_until="networkidle", timeout=60000)
        time.sleep(3)
        screenshot(page, "05_attendance")
        check("Attendance loads", page.locator("body").is_visible())
        check("No console errors on attendance", len(check_console(page)) == 0)

        # ===== 8. Expenses page =====
        print("\n[8] Expenses Page")
        page.goto(f"{FRONTEND}/expenses", wait_until="networkidle", timeout=60000)
        time.sleep(3)
        screenshot(page, "06_expenses")
        check("Expenses loads", page.locator("body").is_visible())
        check("No console errors on expenses", len(check_console(page)) == 0)

        # ===== 9. Goals page =====
        print("\n[9] Goals Page")
        page.goto(f"{FRONTEND}/goals", wait_until="networkidle", timeout=60000)
        time.sleep(3)
        screenshot(page, "07_goals")
        check("Goals loads", page.locator("body").is_visible())
        check("No console errors on goals", len(check_console(page)) == 0)

        # ===== 10. Reports page =====
        print("\n[10] Reports Page")
        page.goto(f"{FRONTEND}/reports", wait_until="networkidle", timeout=60000)
        time.sleep(3)
        screenshot(page, "08_reports")
        check("Reports loads", page.locator("body").is_visible())
        check("No console errors on reports", len(check_console(page)) == 0)

        # ===== 11. Settings page =====
        print("\n[11] Settings Page")
        page.goto(f"{FRONTEND}/settings", wait_until="networkidle", timeout=60000)
        time.sleep(3)
        screenshot(page, "09_settings")
        check("Settings loads", page.locator("body").is_visible())
        check("No console errors on settings", len(check_console(page)) == 0)

        # ===== 12. 404 page =====
        print("\n[12] 404 Page")
        page.goto(f"{FRONTEND}/some-non-existent-page", wait_until="networkidle", timeout=60000)
        time.sleep(2)
        screenshot(page, "10_404")
        page_content = page.content()
        check("404 page shows error code", "404" in page_content)
        check("404 page shows Arabic message", "غير موجود" in page_content or "موجودة" in page_content)

        # ===== 13. XSS protection test =====
        print("\n[13] XSS Protection Test")
        resp = page.request.post(f"{BACKEND}/api/auth/register", data=_json.dumps({
            "username": "<script>alert(1)</script>",
            "email": "xss@test.com",
            "password": "Test1234!"
        }), headers={"Content-Type": "application/json"})
        check("XSS username rejected", resp.status in [400, 422], f"status={resp.status}")

        # ===== 14. Weak password rejection =====
        print("\n[14] Weak Password Test")
        resp = page.request.post(f"{BACKEND}/api/auth/register", data=_json.dumps({
            "username": "weak_test",
            "email": "weak@test.com",
            "password": "short"
        }), headers={"Content-Type": "application/json"})
        check("Weak password rejected", resp.status in [400, 422], f"status={resp.status}")

        # ===== 15. Mobile responsive check =====
        print("\n[15] Mobile Responsive")
        mobile = browser.new_page(viewport={"width": 375, "height": 812})
        mobile.console_logs = []
        mobile.on("console", lambda msg: mobile.console_logs.append(msg))
        mobile.goto(f"{FRONTEND}/login", wait_until="networkidle", timeout=60000)
        time.sleep(3)
        mobile.screenshot(path=os.path.join(OUTPUT, "live_11_mobile.png"), full_page=True)
        print("  Screenshot: mobile")
        mobile_errors = [m for m in mobile.console_logs if m.type == "error"]
        check("Mobile renders without console errors", len(mobile_errors) == 0)
        mobile.close()

        browser.close()

    print(f"\n{'='*50}")
    print(f"Results: {results['passed']} passed / {results['failed']} failed")
    if results["failed"] == 0:
        print("ALL TESTS PASSED!")
    else:
        print(f"{results['failed']} test(s) failed")
    return results

if __name__ == "__main__":
    run_test()
