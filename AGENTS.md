# AGENTS.md — TrackMe (TrackApp)

## Project status
- **No code exists yet.** Phase 1 (MVP) is next: auth + attendance + salary.
- All specs live in `PRD_TrackApp.md` (requirements) and `tasks.md` (breakdown).

## Agent Directives (CRITICAL)
- **Wait for Tech Stack Approval:** Do NOT generate any code until the user explicitly confirms the chosen Frontend framework and Backend language. Ask the user to decide before starting Phase 1.
- **Task-Driven:** Always refer to `tasks.md` for specific task IDs (T001–T035). Do not proceed to the next phase until the current phase is fully tested and approved by the user.

## Key constraints (from PRD)
- **Local only** — no cloud, no internet dependency. Runs on internal network.
- **Multi-user, full data isolation** — every query must scope by `user_id`. No sharing, except for Admins managing users.
- **SQLite** — PRD strongly prefers it. No external DB server needed.
- **Arabic UI** (or bilingual). All user-facing text should support Arabic (RTL support required).
- **Password hashing** required (bcrypt/argon2 — strictly no plaintext, MD5, or SHA).
- **JWT-based auth** for API protection.
- **Currency: USD ($)** — all monetary values in dollars.

## Data model (Confirmed)
*Note: All tables must include `created_at` and `updated_at` timestamps.*
- **Users** (id, username, password_hash, role [admin/employee], salary_type, salary_amount)
- **Attendance** (id, user_id, date, start_time, end_time, hours_worked [DECIMAL], status)
- **Expenses** (id, user_id, date, amount [DECIMAL], category, note)
- **Goals** (id, user_id, name, target_amount [DECIMAL], due_date, saved_amount [DECIMAL])

## Phase structure
1. **M1 — MVP:** Project scaffold, SQLite setup, auth (JWT + bcrypt), user roles setup, attendance CRUD, salary calc.
2. **M2 — Finance:** Expenses CRUD (with custom categories), goals CRUD, savings auto-calc.
3. **M3 — Reports:** Dashboard summaries (weekly/monthly), charts, UI polish, bilingual support.