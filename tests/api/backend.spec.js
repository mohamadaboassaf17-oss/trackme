import { test, expect } from '@playwright/test';

test.setTimeout(90000);

async function registerAndLogin(request) {
  const ts = Date.now();
  const username = `testuser_${ts}`;
  const password = 'TestPass123!';

  await request.post('/api/auth/register', {
    data: { username, password },
  });

  const loginRes = await request.post('/api/auth/login', {
    data: { username, password },
  });
  expect(loginRes.status(), 'Login should succeed').toBe(200);
  const body = await loginRes.json();
  return { username, password, token: body.access_token, loginBody: body };
}

test.describe('Backend Health', () => {
  test('GET /api/health returns status ok', async ({ request }) => {
    await test.step('Call health endpoint', async () => {
      const response = await request.get('/api/health');
      console.log('Health status:', response.status());
      expect(response.status()).toBe(200);

      const body = await response.json();
      console.log('Health body:', JSON.stringify(body));
      expect(body.status).toBe('ok');
      expect(body.message).toContain('TrackMe');
    });
  });
});

test.describe('Authentication', () => {
  test('POST /api/auth/register — register a new user', async ({ request }) => {
    await test.step('Register with unique credentials', async () => {
      const ts = Date.now();
      const username = `testuser_${ts}`;
      const password = 'TestPass123!';

      const response = await request.post('/api/auth/register', {
        data: { username, password },
      });
      console.log('Register status:', response.status());
      expect(response.status()).toBe(201);

      const body = await response.json();
      console.log('Register response:', JSON.stringify(body));
    });
  });

  test('POST /api/auth/login — login with valid credentials', async ({ request }) => {
    await test.step('Register and login', async () => {
      const { token, loginBody } = await registerAndLogin(request);
      expect(token).toBeTruthy();
      expect(loginBody.token_type).toBe('bearer');
      console.log('Login token received, token_type:', loginBody.token_type);
    });
  });

  test('POST /api/auth/login — login with invalid credentials returns 401', async ({ request }) => {
    await test.step('Attempt login with wrong password', async () => {
      const response = await request.post('/api/auth/login', {
        data: { username: 'nonexistent_user_99999', password: 'wrongpass' },
      });
      console.log('Invalid login status:', response.status());
      expect(response.status()).toBe(401);
    });
  });

  test('GET /api/auth/me — get current user with valid token', async ({ request }) => {
    await test.step('Authenticate and fetch user info', async () => {
      const { token } = await registerAndLogin(request);

      const response = await request.get('/api/auth/me', {
        headers: { Authorization: `Bearer ${token}` },
      });
      console.log('/me status:', response.status());
      expect(response.status()).toBe(200);

      const body = await response.json();
      console.log('/me response:', JSON.stringify(body));
    });
  });

  test('GET /api/auth/me — without token returns 401 or 403', async ({ request }) => {
    await test.step('Call /me with no auth header', async () => {
      const response = await request.get('/api/auth/me');
      console.log('/me (no token) status:', response.status());
      expect([401, 403]).toContain(response.status());
    });
  });
});

test.describe('Attendance (Authenticated)', () => {
  let token;

  test.beforeAll(async ({ request }) => {
    const result = await registerAndLogin(request);
    token = result.token;
    console.log('Attendance: authenticated with token');
  });

  test('GET /api/attendance/ — list attendance records', async ({ request }) => {
    await test.step('Fetch attendance list', async () => {
      const response = await request.get('/api/attendance/', {
        headers: { Authorization: `Bearer ${token}` },
      });
      console.log('GET /attendance status:', response.status());
      expect(response.status()).toBe(200);

      const body = await response.json();
      console.log('Attendance records:', JSON.stringify(body));
    });
  });

  test('POST /api/attendance/ — create and verify record', async ({ request }) => {
    await test.step('Create new attendance record', async () => {
      const response = await request.post('/api/attendance/', {
        headers: { Authorization: `Bearer ${token}` },
        data: {
          date: '2026-05-24',
          start_time: '09:00:00',
          end_time: '17:00:00',
          hours_worked: 8,
          status: 'present',
        },
      });
      console.log('POST /attendance status:', response.status());
      expect(response.status()).toBe(201);

      const body = await response.json();
      console.log('Created attendance:', JSON.stringify(body));
    });

    await test.step('Verify record appears in list', async () => {
      const response = await request.get('/api/attendance/', {
        headers: { Authorization: `Bearer ${token}` },
      });
      expect(response.status()).toBe(200);

      const body = await response.json();
      console.log('Attendance after create:', JSON.stringify(body));

      const records = Array.isArray(body) ? body : (body.records || body.data || []);
      const found = records.some(
        (r) => r.date === '2026-05-24' && r.status === 'present',
      );
      expect(found, 'Created attendance record should appear in list').toBe(true);
    });
  });
});

test.describe('Salary (Authenticated)', () => {
  let token;

  test.beforeAll(async ({ request }) => {
    const result = await registerAndLogin(request);
    token = result.token;
  });

  test('GET /api/salary/ — get salary data', async ({ request }) => {
    await test.step('Fetch salary records', async () => {
      const response = await request.get('/api/salary/', {
        headers: { Authorization: `Bearer ${token}` },
      });
      console.log('GET /salary status:', response.status());
      expect(response.status()).toBe(200);

      const body = await response.json();
      console.log('Salary data:', JSON.stringify(body));
    });
  });

  test('PUT /api/users/me — update salary settings', async ({ request }) => {
    await test.step('Update salary type and amount', async () => {
      const response = await request.put('/api/users/me', {
        headers: { Authorization: `Bearer ${token}` },
        data: { salary_type: 'monthly', salary_amount: 5000 },
      });
      console.log('PUT /users/me status:', response.status());
      expect(response.status()).toBe(200);

      const body = await response.json();
      console.log('Updated salary settings:', JSON.stringify(body));
      expect(body.salary_type).toBe('monthly');
      expect(body.salary_amount).toBe(5000);
    });
  });
});

test.describe('Expenses (Authenticated)', () => {
  let token;

  test.beforeAll(async ({ request }) => {
    const result = await registerAndLogin(request);
    token = result.token;
  });

  test('GET /api/expenses/ — list expenses', async ({ request }) => {
    await test.step('Fetch expense list', async () => {
      const response = await request.get('/api/expenses/', {
        headers: { Authorization: `Bearer ${token}` },
      });
      console.log('GET /expenses status:', response.status());
      expect(response.status()).toBe(200);

      const body = await response.json();
      console.log('Expenses:', JSON.stringify(body));
    });
  });

  test('POST /api/expenses/ — create and verify expense', async ({ request }) => {
    await test.step('Create new expense', async () => {
      const response = await request.post('/api/expenses/', {
        headers: { Authorization: `Bearer ${token}` },
        data: {
          amount: 50,
          category: 'طعام',
          note: 'غداء',
          date: '2026-05-24',
        },
      });
      console.log('POST /expenses status:', response.status());
      expect(response.status()).toBe(201);

      const body = await response.json();
      console.log('Created expense:', JSON.stringify(body));
    });

    await test.step('Verify expense appears in list', async () => {
      const response = await request.get('/api/expenses/', {
        headers: { Authorization: `Bearer ${token}` },
      });
      expect(response.status()).toBe(200);

      const body = await response.json();
      const expenses = Array.isArray(body) ? body : (body.expenses || body.data || []);
      const found = expenses.some(
        (e) => e.amount === 50 && e.category === 'طعام' && e.date === '2026-05-24',
      );
      expect(found, 'Created expense should appear in list').toBe(true);
    });
  });
});

test.describe('Goals (Authenticated)', () => {
  let token;

  test.beforeAll(async ({ request }) => {
    const result = await registerAndLogin(request);
    token = result.token;
  });

  test('GET /api/goals/ — list goals', async ({ request }) => {
    await test.step('Fetch goal list', async () => {
      const response = await request.get('/api/goals/', {
        headers: { Authorization: `Bearer ${token}` },
      });
      console.log('GET /goals status:', response.status());
      expect(response.status()).toBe(200);

      const body = await response.json();
      console.log('Goals:', JSON.stringify(body));
    });
  });

  test('POST /api/goals/ — create and verify goal', async ({ request }) => {
    await test.step('Create new goal', async () => {
      const response = await request.post('/api/goals/', {
        headers: { Authorization: `Bearer ${token}` },
        data: {
          name: 'توفير',
          target_amount: 5000,
          saved_amount: 1000,
          due_date: '2026-12-31',
        },
      });
      console.log('POST /goals status:', response.status());
      expect(response.status()).toBe(201);

      const body = await response.json();
      console.log('Created goal:', JSON.stringify(body));
    });

    await test.step('Verify goal appears in list', async () => {
      const response = await request.get('/api/goals/', {
        headers: { Authorization: `Bearer ${token}` },
      });
      expect(response.status()).toBe(200);

      const body = await response.json();
      const goals = Array.isArray(body) ? body : (body.goals || body.data || []);
      const found = goals.some(
        (g) => g.name === 'توفير' && g.target_amount === 5000,
      );
      expect(found, 'Created goal should appear in list').toBe(true);
    });
  });
});

test.describe('Settings (Authenticated)', () => {
  let token;

  test.beforeAll(async ({ request }) => {
    const result = await registerAndLogin(request);
    token = result.token;
  });

  test('GET /api/settings/shift-defaults — get shift defaults', async ({ request }) => {
    await test.step('Fetch shift defaults', async () => {
      const response = await request.get('/api/settings/shift-defaults', {
        headers: { Authorization: `Bearer ${token}` },
      });
      console.log('GET /settings/shift-defaults status:', response.status());
      expect(response.status()).toBe(200);

      const body = await response.json();
      console.log('Shift defaults:', JSON.stringify(body));
    });
  });

  test('PUT /api/settings/shift-defaults — update and verify shift defaults', async ({ request }) => {
    await test.step('Update shift times', async () => {
      const response = await request.put('/api/settings/shift-defaults', {
        headers: { Authorization: `Bearer ${token}` },
        data: {
          default_start_time: '08:00',
          default_end_time: '16:00',
        },
      });
      console.log('PUT /settings/shift-defaults status:', response.status());
      expect(response.status()).toBe(200);

      const body = await response.json();
      console.log('Updated shift defaults:', JSON.stringify(body));
    });

    await test.step('Verify settings were updated', async () => {
      const response = await request.get('/api/settings/shift-defaults', {
        headers: { Authorization: `Bearer ${token}` },
      });
      expect(response.status()).toBe(200);

      const body = await response.json();
      console.log('Shift defaults after update:', JSON.stringify(body));

      const shiftStart = body.default_start_time || null;
      const shiftEnd = body.default_end_time || null;
      expect(shiftStart, 'default_start_time should match').toBe('08:00');
      expect(shiftEnd, 'default_end_time should match').toBe('16:00');
    });
  });
});
