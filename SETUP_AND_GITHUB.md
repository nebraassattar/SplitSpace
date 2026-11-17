# SplitSpace — Milestones 2 and 3 delivery

## What to copy

This ZIP is an **overlay** for the existing GitHub repository, not a replacement. Keep existing `backend/models.py`, `frontend/package.json`, `frontend/src/main.tsx`, `frontend/vite.config.ts`, `specifications.md`, `wireframes.md`, and all existing configuration.

Copy the contents of this ZIP into the root of the cloned SplitSpace repository, preserving directories. Overwrite `backend/app.py`, `backend/requirements.txt`, `backend/.env.example`, `frontend/src/App.tsx`, and `frontend/src/index.css`. Add the new `backend/api.py`, `backend/Procfile`, `backend/tests/test_workflows.py`, `.gitignore`, and this guide. **Do not delete other files.**

## Supabase

1. Create a Supabase project at https://supabase.com/dashboard.
2. In **Connect**, copy the PostgreSQL **session pooler** URI (or the recommended URI for your network). Use the exact host, port, username and password shown.
3. In `backend/`, copy `.env.example` to `.env`.
4. Change the URI scheme from `postgresql://` to `postgresql+psycopg://`, and put the resulting URI in `DATABASE_URL`.
5. Generate a secret with `python3 -c "import secrets; print(secrets.token_hex(32))"` and use it as `SECRET_KEY`.
6. Never commit `.env`.

## Run on Mac (two terminals)

Terminal 1:
```bash
cd SplitSpace/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app app run --port 5001 --debug
```

Terminal 2:
```bash
cd SplitSpace/frontend
npm install
npm run dev
```

Open http://localhost:5173. The Vite proxy already forwards `/api` to port 5001 in the original project.

## Tests

```bash
cd SplitSpace/backend
.venv/bin/python -m pytest
```

Tests use SQLite in memory, not Supabase. Run them before opening a pull request.

## GitHub — recommended terminal method

```bash
git clone https://github.com/nebraassattar/SplitSpace.git
cd SplitSpace
git switch -c anusha/milestones-2-3
# Copy all overlay files into this folder, preserving their paths.
git status
# Make sure backend/.env is NOT staged
git add .
git status
git commit -m "Implement accounts, households, expenses, balances, chores and dashboard"
git push -u origin anusha/milestones-2-3
```

Open https://github.com/nebraassattar/SplitSpace/pulls and click **New pull request**, base `main`, compare `anusha/milestones-2-3`. Ask teammates to review; avoid pushing to main directly.

## GitHub — web interface alternative

In the repository select the branch dropdown > **View all branches** > **New branch** from `main`. On that branch use **Add file > Upload files** to upload the files into the correct directories (GitHub's upload interface may require navigating into each directory). For overwriting existing files, open the file, choose Edit, replace the contents, and commit to your branch. The terminal method is less error-prone.

## Production deployment

- Supabase hosts the persistent database.
- Deploy Flask to a Python host such as Render, root directory `backend`, build command `pip install -r requirements.txt`, start command `gunicorn 'app:app' --bind 0.0.0.0:$PORT`.
- Set `DATABASE_URL`, `SECRET_KEY`, `COOKIE_SECURE=true`, and `ALLOWED_ORIGINS` on the backend host. Do not enable Flask debug mode.
- Deploy Vite to Vercel, root directory `frontend`, build `npm run build`, output `dist`.
- Configure a **same-origin `/api/*` reverse proxy** from the frontend domain to the Flask host (e.g. Vercel rewrites) to keep Flask session cookies working. Do not point browser code at Supabase database credentials.
- Configure a SPA fallback for routes if introducing browser history routing later.
- Run the live smoke test: register, create/join household, add expense, record settlement, add/complete chore, refresh page, confirm data persists.

## Caveats

This delivery has been syntax-checked but **not run end-to-end against your Supabase project**. Actual deployment and live integration testing are still required. This is an MVP; before handling sensitive real-world information, add rate limiting, stronger CSRF defenses, migrations, security monitoring, and a production review. `db.create_all()` creates missing tables but does not migrate existing tables.
