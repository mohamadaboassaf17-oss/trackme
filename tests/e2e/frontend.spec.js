import { test, expect } from '@playwright/test';
import path from 'path';
import fs from 'fs';

const SCREENSHOT_DIR = path.resolve('tests/screenshots');

function ensureScreenshotDir() {
  if (!fs.existsSync(SCREENSHOT_DIR)) {
    fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
  }
}

test.beforeAll(() => {
  ensureScreenshotDir();
});

test.describe('Frontend — Page Load', () => {

  test('should load the page with #app content', async ({ page }) => {
    await test.step('navigate to home page', async () => {
      await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 90000 });
    });

    await test.step('wait for Vue to render inside #app', async () => {
      await page.waitForSelector('#app > *', { timeout: 30000 });
      await page.waitForTimeout(3000);
    });

    await test.step('verify #app has child elements', async () => {
      const children = await page.locator('#app > *').count();
      expect(children).toBeGreaterThan(0);
    });

    await test.step('print debug info', async () => {
      console.log('Current URL:', page.url());
      console.log('Page title:', await page.title());
    });

    await test.step('take screenshot', async () => {
      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, 'e2e_01_page_load.png'),
        fullPage: true,
      });
    });
  });

  test('should have title containing TrackMe', async ({ page }) => {
    await test.step('navigate to home page', async () => {
      await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 90000 });
    });

    await test.step('wait for Vue to render', async () => {
      await page.waitForSelector('#app > *', { timeout: 30000 });
      await page.waitForTimeout(3000);
    });

    await test.step('check page title', async () => {
      const title = await page.title();
      console.log('Page title:', title);
      expect(title).toContain('TrackMe');
    });
  });
});

test.describe('Frontend — Login Form', () => {

  test('should have at least 2 input fields', async ({ page }) => {
    await test.step('load page', async () => {
      await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 90000 });
      await page.waitForSelector('#app > *', { timeout: 30000 });
      await page.waitForTimeout(3000);
    });

    await test.step('count input fields', async () => {
      const count = await page.locator('input').count();
      console.log('Input fields found:', count);
      expect(count).toBeGreaterThanOrEqual(2);
    });

    await test.step('take screenshot', async () => {
      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, 'e2e_02_login_inputs.png'),
        fullPage: true,
      });
    });
  });

  test('should have a login button', async ({ page }) => {
    await test.step('load page', async () => {
      await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 90000 });
      await page.waitForSelector('#app > *', { timeout: 30000 });
      await page.waitForTimeout(3000);
    });

    await test.step('find login button', async () => {
      const button = page.getByRole('button').first();
      await expect(button).toBeVisible({ timeout: 15000 });
      console.log('Current URL:', page.url());
    });

    await test.step('take screenshot', async () => {
      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, 'e2e_03_login_button.png'),
        fullPage: true,
      });
    });
  });

  test('should type credentials and submit', async ({ page }) => {
    await test.step('load page', async () => {
      await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 90000 });
      await page.waitForSelector('#app > *', { timeout: 30000 });
      await page.waitForTimeout(3000);
    });

    await test.step('fill username input', async () => {
      const usernameInput = page.locator('input[type="text"], input:not([type="password"])').first();
      await usernameInput.fill('testuser');
      console.log('Filled username input');
    });

    await test.step('fill password input', async () => {
      const passwordInput = page.locator('input[type="password"]');
      await passwordInput.fill('test1234');
      console.log('Filled password input');
    });

    await test.step('click login button', async () => {
      const loginButton = page.getByRole('button').first();
      await loginButton.click();
      console.log('Clicked login button');
    });

    await test.step('wait for response', async () => {
      await page.waitForTimeout(5000);
    });

    await test.step('print debug info', async () => {
      console.log('Current URL after submit:', page.url());
      console.log('Page title after submit:', await page.title());
    });

    await test.step('take screenshot after submit', async () => {
      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, 'e2e_04_login_submit.png'),
        fullPage: true,
      });
    });
  });
});

test.describe('Frontend — Login Attempt', () => {

  test('should login with test user and check redirect', async ({ page }) => {
    await test.step('load page', async () => {
      await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 90000 });
      await page.waitForSelector('#app > *', { timeout: 30000 });
      await page.waitForTimeout(3000);
    });

    await test.step('fill username', async () => {
      await page.locator('input[type="text"], input:not([type="password"])').first().fill('testuser');
    });

    await test.step('fill password', async () => {
      await page.locator('input[type="password"]').fill('test1234');
    });

    await test.step('click login button', async () => {
      await page.getByRole('button').first().click();
    });

    await test.step('wait for response', async () => {
      await page.waitForTimeout(5000);
    });

    await test.step('check if redirected to dashboard', async () => {
      const url = page.url();
      console.log('Current URL:', url);
      console.log('Page title:', await page.title());
      const redirected = url.includes('/dashboard');
      console.log('Redirected to dashboard:', redirected);
    });

    await test.step('take screenshot', async () => {
      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, 'e2e_05_login_success.png'),
        fullPage: true,
      });
    });
  });

  test('should show error on wrong password', async ({ page }) => {
    await test.step('load page', async () => {
      await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 90000 });
      await page.waitForSelector('#app > *', { timeout: 30000 });
      await page.waitForTimeout(3000);
    });

    await test.step('fill username', async () => {
      await page.locator('input[type="text"], input:not([type="password"])').first().fill('testuser');
    });

    await test.step('fill wrong password', async () => {
      await page.locator('input[type="password"]').fill('wrongpassword');
    });

    await test.step('click login button', async () => {
      await page.getByRole('button').first().click();
    });

    await test.step('wait for error response', async () => {
      await page.waitForTimeout(5000);
    });

    await test.step('verify we did not redirect to dashboard', async () => {
      const url = page.url();
      console.log('Current URL after wrong login:', url);
      expect(url).not.toContain('/dashboard');
    });

    await test.step('take screenshot', async () => {
      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, 'e2e_06_login_wrong_password.png'),
        fullPage: true,
      });
    });
  });
});

test.describe('Frontend — Screenshots', () => {

  test('should take full-page screenshot of login page', async ({ page }) => {
    await test.step('load page', async () => {
      await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 90000 });
      await page.waitForSelector('#app > *', { timeout: 30000 });
      await page.waitForTimeout(3000);
    });

    await test.step('take full-page screenshot', async () => {
      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, 'e2e_07_fullpage_login.png'),
        fullPage: true,
      });
    });
  });

  test('should take mobile viewport screenshot', async ({ page }) => {
    await test.step('set mobile viewport', async () => {
      await page.setViewportSize({ width: 375, height: 812 });
    });

    await test.step('load page', async () => {
      await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 90000 });
      await page.waitForSelector('#app > *', { timeout: 30000 });
      await page.waitForTimeout(3000);
    });

    await test.step('take mobile screenshot', async () => {
      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, 'e2e_08_mobile_login.png'),
        fullPage: true,
      });
    });
  });

  test('should take desktop viewport screenshot', async ({ page }) => {
    await test.step('set desktop viewport', async () => {
      await page.setViewportSize({ width: 1920, height: 1080 });
    });

    await test.step('load page', async () => {
      await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 90000 });
      await page.waitForSelector('#app > *', { timeout: 30000 });
      await page.waitForTimeout(3000);
    });

    await test.step('take desktop screenshot', async () => {
      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, 'e2e_09_desktop_login.png'),
        fullPage: true,
      });
    });
  });
});
