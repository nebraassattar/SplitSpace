# SplitSpace - TODO

Owners: **N** = Nebraas, **G** = George, **A** = Anusha, **All** = shared.
See `specifications.md` for details on every item.

## Milestone 1 - Planning and setup (this week)

- [x] Write `specifications.md`: scope, user stories, screens, business rules, data model, API contracts (All)
- [x] Write `TODO.md` (All)
- [ ] Team review of `specifications.md`; resolve open questions in section 10 (All)
- [x] Repo setup: `frontend/` (React + TypeScript), `backend/` (Flask + SQLAlchemy), local PostgreSQL, `.gitignore`, README with run instructions (All)
- [ ] Agree on workflow: drafted in README, needs team sign-off (All)
- [ ] Add all three members as repo collaborators (N)
- [x] Rough wireframes for the 8 screens in spec section 4: `wireframes.md`, Anusha to review (A)

## Milestone 2 - Accounts and households

- [x] Database tables: users, households, memberships (`backend/models.py`) (G)
- [ ] Register / login / logout / me endpoints, password hashing (G)
- [ ] Create household, join by invite code, list my households, get household (G)
- [ ] Server-side membership check reused by every `/api/households/:hid/...` route (G)
- [ ] Login, Register, My households, Members screens (G)
- [ ] Redirect logged-out users to `/login` (G)
- [ ] Tests: auth success/failure, duplicate email, bad invite code, non-member gets 404 (G)
- [ ] Early deployment with a persistent database (All)

## Milestone 3 - Core workflows

### Expenses, balances, settlements (N)

- [x] Tables: expenses, expense_shares, settlements (`backend/models.py`)
- [ ] Equal-split function in integer cents (spec 5.1)
- [ ] Expense CRUD endpoints with creator/owner permissions
- [ ] Balance calculation (spec 5.2) and `/balances` endpoint
- [ ] Settlement create/list/delete with amount-not-above-debt check
- [ ] Expenses screen and Balances screen
- [ ] Tests: split rounding, payer not a participant, edit/delete recomputes, partial settlement, worked example from spec section 3

### Chores and dashboard (A)

- [x] Table: chores (`backend/models.py`)
- [ ] Chore CRUD endpoints, mark done / undo
- [ ] Chores screen with open/done tabs and overdue highlighting
- [ ] Dashboard screen (my balance, my open chores, 5 recent expenses)
- [ ] Tests: chore permissions, assignee must be a member, status filter

## Milestone 4 - Integration, testing, final delivery

- [ ] Multi-account test: 3 members + 1 outsider, run worked example end to end (All)
- [ ] Cross-household privacy test on every endpoint (G)
- [ ] Calculation edge cases review (N)
- [ ] Mobile layout pass at 360px on every screen (A)
- [ ] Final deployment and smoke test on the live URL (All)
- [ ] README: live URL, setup, how AI tools were used and verified (All)
- [ ] Demo script and presentation (All)

## Stretch (only after MVP is done)

- [ ] Unequal splits
- [ ] Debt simplification
- [ ] Recurring chores / expenses
- [ ] Leave household / remove member
