import { defineConfig, devices } from '@playwright/test';

const BACKEND_URL = process.env.BACKEND_URL || 'https://trackme-backend-xena.onrender.com';
const FRONTEND_URL = process.env.FRONTEND_URL || 'https://trackme-ugq1.onrender.com';

export default defineConfig({
  testDir: './tests',
  fullyParallel: false,
  retries: 1,
  workers: 1,
  reporter: [['list'], ['html', { open: 'never' }]],
  
  timeout: 60000,
  expect: { timeout: 15000 },

  use: {
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  projects: [
    {
      name: 'api',
      testMatch: '**/api/**/*.spec.js',
      use: {
        baseURL: BACKEND_URL,
      },
    },
    {
      name: 'e2e',
      testMatch: '**/e2e/**/*.spec.js',
      use: {
        ...devices['Desktop Chrome'],
        baseURL: FRONTEND_URL,
        launchOptions: {
          args: ['--disable-web-security'],
        },
      },
    },
  ],
});
