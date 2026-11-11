# SplitSpace

Shared expenses and household chores for roommates. CSE 4095, Team 6: Nebraas Sattar, George Ji, Anusha Prabhakar.

- [specifications.md](specifications.md): what we're building (features, rules, data model, API)
- [TODO.md](TODO.md): tasks by milestone and owner
- [wireframes.md](wireframes.md): screen layouts

## Stack

React + TypeScript (`frontend/`), Python + Flask (`backend/`), PostgreSQL + SQLAlchemy.

## Run locally

Prerequisites: Python 3.12+, Node 20+, PostgreSQL.

**Database** (once):

```sh
createdb splitspace
```

**Backend** (terminal 1):

```sh
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit DATABASE_URL if your Postgres needs a user/password:
                       # postgresql+psycopg://USER:PASSWORD@localhost/splitspace
flask --app app run --port 5001 --debug
```

Tables are created automatically on startup. Port 5001 because macOS uses 5000 for AirPlay.

**Frontend** (terminal 2):

```sh
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The page should say `API: ok`. Vite forwards `/api/*` to Flask on port 5001.

**Tests:**

```sh
cd backend && .venv/bin/python -m pytest
```

## Team workflow (proposed, needs team sign-off)

1. Pick a task from `TODO.md`. Create a branch off `main` named `<your-name>/<short-task>` (e.g. `george/login-api`).
2. Keep PRs small: one task per PR. Update `TODO.md` checkboxes in the same PR.
3. If your change touches an API shape or a table, update `specifications.md` in the same PR.
4. At least one teammate reviews and approves before merging. Don't push directly to `main`.
5. Backend tests must pass before merging.
6. Never commit `.env` or passwords.
