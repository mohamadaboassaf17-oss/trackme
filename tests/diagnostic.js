const { chromium } = require('playwright');
const path = require('path');

const FRONTEND = process.env.FRONTEND_URL || 'https://trackme-ugq1.onrender.com';
const BACKEND = process.env.BACKEND_URL || 'https://trackme-backend-xena.onrender.com/api';
const SCREENSHOTS = path.join(__dirname, 'screenshots');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 900 },
    locale: 'ar-SA'
  });
  const page = await context.newPage();

  // Collect ALL data
  const networkRequests = [];
  const networkErrors = [];
  const consoleMessages = [];
  const pageErrors = [];

  page.on('request', req => {
    networkRequests.push({ url: req.url(), method: req.method(), type: req.resourceType() });
  });
  page.on('response', resp => {
    if (resp.status() >= 400) {
      networkErrors.push({ url: resp.url(), status: resp.status(), method: resp.request().method() });
    }
  });
  page.on('console', msg => {
    consoleMessages.push(`[${msg.type()}] ${msg.text()}`);
  });
  page.on('pageerror', err => {
    pageErrors.push(err.message);
  });

  console.log('╔══════════════════════════════════════════╗');
  console.log('║   DEEP DIAGNOSTIC TEST - Render Deploy  ║');
  console.log('╚══════════════════════════════════════════╝');
  console.log(`Frontend: ${FRONTEND}`);
  console.log(`Backend:  ${BACKEND}`);
  console.log('');

  // ============================================
  // STEP 1: Load login page with network monitoring
  // ============================================
  console.log('[STEP 1] Loading login page...');
  try {
    await page.goto(FRONTEND + '/login', { waitUntil: 'domcontentloaded', timeout: 90000 });
    console.log('  -> Page loaded, waiting 5s for render...');
    await page.waitForTimeout(5000);
    await page.waitForSelector('#app > *', { timeout: 30000 }).catch(() => {
      console.log('  -> WARNING: #app has no children yet');
    });
    await page.waitForTimeout(3000);
  } catch (e) {
    console.log(`  -> ERROR loading page: ${e.message}`);
  }

  const title = await page.title();
  console.log(`  -> Title: "${title}"`);
  console.log(`  -> URL: ${page.url()}`);

  // Count UI elements
  const inputCount = await page.locator('input').count();
  const buttonCount = await page.locator('button').count();
  const selectCount = await page.locator('select').count();
  console.log(`  -> Found: ${inputCount} inputs, ${buttonCount} buttons, ${selectCount} selects`);

  // Check if login form is visible
  const loginFormVisible = await page.locator('form').first().isVisible().catch(() => false);
  console.log(`  -> Login form visible: ${loginFormVisible}`);

  await page.screenshot({ path: path.join(SCREENSHOTS, 'diag_01_login.png'), fullPage: true });

  // ============================================
  // STEP 2: Try to login with test credentials
  // ============================================
  console.log('');
  console.log('[STEP 2] Attempting login...');
  
  const ts = Date.now().toString().slice(-6);
  const username = `testuser_${ts}`;
  const password = 'Test1234!';

  // Click "register new account" first since we need a user
  const registerLink = page.locator('text=إنشاء حساب جديد');
  const regLinkVisible = await registerLink.isVisible().catch(() => false);
  console.log(`  -> Register link visible: ${regLinkVisible}`);

  if (regLinkVisible) {
    await registerLink.click();
    await page.waitForTimeout(2000);
    await page.screenshot({ path: path.join(SCREENSHOTS, 'diag_02_register_modal.png'), fullPage: true });

    // Check registration form fields
    const regFields = ['#reg-username', '#reg-password', '#salary-type', '#salary-amount'];
    for (const f of regFields) {
      const v = await page.locator(f).isVisible().catch(() => false);
      console.log(`  -> ${f} visible: ${v}`);
    }

    // Try to register
    const regUsername = page.locator('#reg-username');
    const regPassword = page.locator('#reg-password');
    
    if (await regUsername.isVisible()) {
      await regUsername.fill(username);
      await regPassword.fill(password);
      console.log(`  -> Filled registration form with username: ${username}`);
      
      // Click the register submit button
      const regSubmit = page.locator('form').filter({ hasText: 'إنشاء حساب' }).locator('button[type="submit"]');
      if (await regSubmit.isVisible()) {
        await regSubmit.click();
        console.log('  -> Clicked register button');
        await page.waitForTimeout(5000);
        console.log(`  -> URL after register: ${page.url()}`);
        await page.screenshot({ path: path.join(SCREENSHOTS, 'diag_03_after_register.png'), fullPage: true });
      }
    }
  }

  // Check what API calls were made
  console.log('');
  console.log('[STEP 3] Network Analysis:');
  const apiCalls = networkRequests.filter(r => r.url.includes('trackme-backend'));
  console.log(`  -> Total API calls to backend: ${apiCalls.length}`);
  for (const c of apiCalls) {
    console.log(`     ${c.method} ${c.url.replace(BACKEND.replace('/api',''), '')}`);
  }

  console.log(`  -> Failed requests (4xx/5xx): ${networkErrors.length}`);
  for (const e of networkErrors) {
    console.log(`     [${e.status}] ${e.method} ${e.url}`);
  }

  console.log(`  -> Console messages: ${consoleMessages.length}`);
  const consoleErrors = consoleMessages.filter(m => m.includes('[error]'));
  for (const ce of consoleErrors.slice(0, 10)) {
    console.log(`     ${ce}`);
  }

  console.log(`  -> Page errors: ${pageErrors.length}`);
  for (const pe of pageErrors) {
    console.log(`     ${pe}`);
  }

  // ============================================
  // STEP 4: Summary & Diagnosis
  // ============================================
  console.log('');
  console.log('═══════════════════════════════════════════');
  console.log('DIAGNOSIS SUMMARY:');
  console.log('═══════════════════════════════════════════');

  const issues = [];

  // Check if API baseURL has /api
  const rawBackendCalls = apiCalls.filter(r => r.url.includes('/auth/') || r.url.includes('/attendance/') || r.url.includes('/expenses/'));
  const missingApiPrefix = rawBackendCalls.filter(r => {
    const u = new URL(r.url);
    return !u.pathname.startsWith('/api/');
  });
  if (missingApiPrefix.length > 0) {
    issues.push('CRITICAL: API calls missing /api prefix! Backend will return 404.');
    for (const c of missingApiPrefix) {
      console.log(`  -> ${c.method} ${c.url}`);
    }
  }

  if (networkErrors.length > 0) {
    const dbErrors = networkErrors.filter(e => e.url.includes('/api/'));
    issues.push(`Found ${networkErrors.length} failed network requests (${dbErrors.length} from backend API)`);
  }

  if (pageErrors.length > 0) {
    issues.push(`Found ${pageErrors.length} page-level JavaScript errors`);
  }

  if (!loginFormVisible) {
    issues.push('Login form not found or not visible');
  }

  if (issues.length === 0) {
    console.log('No critical issues found!');
  } else {
    for (let i = 0; i < issues.length; i++) {
      console.log(`  ${i+1}. ${issues[i]}`);
    }
  }

  // Save diagnostic report
  const report = {
    timestamp: new Date().toISOString(),
    frontend: FRONTEND,
    backend: BACKEND,
    api_calls: apiCalls.map(r => ({ method: r.method, url: r.url, type: r.type })),
    network_errors: networkErrors,
    console_messages: consoleMessages.slice(-30),
    page_errors: pageErrors,
    issues: issues,
    ui_elements: { inputs: inputCount, buttons: buttonCount, selects: selectCount, login_form_visible: loginFormVisible }
  };

  const fs = require('fs');
  fs.writeFileSync(path.join(__dirname, 'diagnostic_report.json'), JSON.stringify(report, null, 2));
  console.log('');
  console.log('Report saved to tests/diagnostic_report.json');

  await browser.close();
  console.log('DONE');
})();
