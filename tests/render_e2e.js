const { chromium } = require('playwright');
const path = require('path');
const http = require('http');

const FRONTEND = 'https://trackme-ugq1.onrender.com';
const BACKEND = 'https://trackme-backend-xena.onrender.com/api';

function apiCall(method, url, data, token) {
  return new Promise((resolve, reject) => {
    const u = new URL(url);
    const opts = {
      hostname: u.hostname, port: 443, path: u.pathname,
      method, headers: { 'Content-Type': 'application/json' }
    };
    if (token) opts.headers['Authorization'] = 'Bearer ' + token;
    const req = require('https').request(opts, res => {
      let body = '';
      res.on('data', c => body += c);
      res.on('end', () => {
        try { resolve({ status: res.statusCode, data: JSON.parse(body) }); }
        catch { resolve({ status: res.statusCode, body }); }
      });
    });
    req.on('error', e => resolve({ status: 0, error: e.message }));
    if (data) req.write(JSON.stringify(data));
    req.end();
  });
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', m => { if (m.type()==='error') errors.push(m.text()); });

  let passed = 0, failed = 0;
  function T(name, cond, detail) {
    if (cond) { passed++; console.log('  [PASS]', name); }
    else { failed++; console.log('  [FAIL]', name, detail||''); }
  }

  console.log('RENDER DEPLOYED TEST');
  console.log('===================\n');

  // 1. API: Register + Login
  console.log('--- API Tests ---');
  const ts = Date.now().toString().slice(-6);
  const u = 'rendertest_'+ts, p = 'Test1234!';
  const r1 = await apiCall('POST', BACKEND+'/auth/register', {username:u, password:p});
  T('Register', r1.status===201);

  const r2 = await apiCall('POST', BACKEND+'/auth/login', {username:u, password:p});
  const token = r2.data?.access_token;
  T('Login', !!token);

  const r3 = await apiCall('POST', BACKEND+'/attendance/', {
    date:'2026-05-24',start_time:'09:00:00',end_time:'17:00:00',hours_worked:8,status:'present'
  }, token);
  T('Attendance create', r3.status===201);
  T('start_time saved', r3.data?.start_time==='09:00:00');

  const r4 = await apiCall('PUT', BACKEND+'/attendance/'+r3.data?.id, {end_time:'18:00:00'}, token);
  T('hours_worked auto-calc', r4.data?.hours_worked>=9, 'Got:'+r4.data?.hours_worked);

  const r5 = await apiCall('POST', BACKEND+'/wealth/', {
    date:'2026-05-24',source:'Salary',amount:3000
  }, token);
  T('Wealth create', r5.status===201, 'Status:'+r5.status);

  // 2. Browser: Load frontend
  console.log('\n--- Browser Tests ---');
  try {
    // Load root (SPA should handle this)
    await page.goto(FRONTEND+'/', {waitUntil:'domcontentloaded',timeout:90000});
    await page.waitForTimeout(5000);
    await page.waitForSelector('#app > *', {timeout:30000}).catch(()=>{});
    await page.waitForTimeout(3000);
    
    const title = await page.title();
    T('Page loads', title.includes('TrackMe'), title);
    T('App renders', (await page.locator('input').count()) >= 2, 'Inputs:'+await page.locator('input').count());
    
    await page.screenshot({path:'tests/screenshots/render_test_root.png',fullPage:true});

    // Try login via browser (root should redirect to /login via SPA router)
    const inputs = await page.locator('input[type=\"text\"], input:not([type=\"password\"])').count();
    if (inputs >= 1) {
      await page.locator('input[type=\"text\"], input:not([type=\"password\"])').first().fill(u);
      await page.locator('input[type=\"password\"]').fill(p);
      await page.locator('button[type=\"submit\"]').first().click();
      await page.waitForTimeout(8000);
      
      const url = page.url();
      T('Login redirect to dashboard', url.includes('dashboard'), url);
      await page.screenshot({path:'tests/screenshots/render_test_dashboard.png',fullPage:true});
    } else {
      T('Login form visible', false, 'No inputs found - SPA routing broken on /login');
    }
  } catch(e) {
    T('Browser test', false, e.message);
  }

  console.log('\n===================');
  console.log('RENDER RESULTS: '+passed+'/'+(passed+failed)+' passed');
  if (failed) console.log('FAILURES: '+failed+ ' (SPA routing needs manual fix on Render dashboard)');
  else console.log('ALL RENDER TESTS PASSED!');

  console.log('Browser errors: '+errors.length);
  await browser.close();
})();
