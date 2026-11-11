# SplitSpace - Specifications

SplitSpace gives roommates a shared record of expenses, balances, and chores.

Team 6 (CSE 4095): Nebraas Sattar, George Ji, Anusha Prabhakar

## 1. Scope

### MVP features

| # | Feature | Owner |
|---|---------|-------|
| F1 | Accounts and households: register, log in, create or join a household with an invite code | George |
| F2 | Shared expenses: record a payer and split equally among selected members | Nebraas |
| F3 | Balances and settlements: see who owes whom, record payments made outside the app | Nebraas |
| F4 | Chore management: assign chores with due dates, track completion | Anusha |
| F5 | Dashboard: one-page summary of balances, my chores, recent expenses | Anusha |

Shared: database design, code reviews, testing, deployment, demo.

### Out of scope for MVP (stretch)

- Unequal splits (by amount, percentage, or shares)
- Debt simplification (minimizing the number of payments across the household)
- Recurring expenses and recurring chores
- Leaving a household, removing members, transferring ownership
- Notifications (email, push)
- Receipt uploads
- Real payment processing (settlements are records only)
- Multiple currencies

## 2. Users and roles

- **Visitor**: not logged in. Can only register or log in.
- **Member**: belongs to a household. Can view all of that household's records and create expenses, settlements, and chores.
- **Owner**: the member who created the household. Same as member, plus can edit or delete any record in the household.

A user may belong to more than one household. Every household record is visible only to that household's members.

## 3. User stories and acceptance criteria

### F1 Accounts and households

- As a visitor I can register with email, display name, and password.
  - Email is unique (case-insensitive). Password is at least 8 characters.
  - Passwords are stored hashed, never in plain text.
- As a visitor I can log in and stay logged in until I log out.
  - Wrong email or password returns one generic error (does not reveal which was wrong).
- As a member I can create a household with a name. I become its owner and get an invite code.
- As a member I can join a household by entering its invite code.
  - Invite codes are 8 characters, random, unique. Invalid code shows an error.
  - Joining a household I already belong to is a no-op, not an error.
- As a member I can see my households and each one's member list.

### F2 Shared expenses

- As a member I can add an expense: description, total amount, date, payer (any member), participants (one or more members, payer may or may not be included).
- The amount is split equally among participants (see 5.1 for rounding).
- As a member I can see the household's expenses, newest first, with payer, amount, participants, and each participant's share.
- The creator of an expense, or the owner, can edit or delete it. Editing recomputes the shares. Balances update immediately.

### F3 Balances and settlements

- As a member I can see every outstanding debt in the household in the form "A owes B $X".
- As a member I can record a settlement: "A paid B $X" on a date, with an optional note.
  - Only the two people involved (A or B) or the owner can record it.
  - Amount must be greater than 0 and no more than what A currently owes B.
- As a member I can see the settlement history.
- The creator of a settlement, or the owner, can delete it. Balances update immediately.

### F4 Chores

- As a member I can create a chore: title, assignee (any member), due date.
- As a member I can mark a chore done, or undo that.
- As a member I can filter chores to open / done and see overdue open chores highlighted.
- The creator of a chore, or the owner, can edit or delete it.

### F5 Dashboard

- After picking a household, I land on a dashboard showing:
  - my net balance and the debts that involve me,
  - my open chores, soonest due first, overdue highlighted,
  - the 5 most recent expenses.

### Worked example (from the proposal)

1. Nebraas pays $60.00 for groceries, participants Nebraas, George, Anusha. Shares: $20.00 each.
2. Balances: George owes Nebraas $20.00. Anusha owes Nebraas $20.00.
3. George records a $20.00 settlement to Nebraas.
4. Balances: George owes $0. Anusha still owes Nebraas $20.00.

This example must pass as an automated test.

## 4. Screens

| Screen | Path | Contents |
|--------|------|----------|
| Login | `/login` | Email, password, link to register |
| Register | `/register` | Email, display name, password |
| My households | `/households` | List of my households; "Create household" form; "Join with code" form |
| Dashboard | `/households/:id` | F5 summary; nav to the screens below |
| Expenses | `/households/:id/expenses` | Expense list; add / edit form (description, amount, date, payer dropdown, participant checkboxes, all checked by default) |
| Balances | `/households/:id/balances` | "A owes B $X" list; "Record payment" form prefilled from a debt row; settlement history |
| Chores | `/households/:id/chores` | Open / done tabs; add / edit form (title, assignee, due date); done checkbox |
| Members | `/households/:id/members` | Member list with roles; invite code with copy button |

Navigation: logged-out users are redirected to `/login`. Visiting a household you don't belong to shows "Not found". Layout must be usable at phone width (360px).

## 5. Business rules

### 5.1 Money

- All amounts are stored and transmitted as **integer cents**. No floating point anywhere in money math.
- The UI accepts dollars (e.g. `12.34`), converts to cents, and rejects more than 2 decimal places, zero, or negative values.
- **Equal split**: `base = amount // n`, `remainder = amount % n`. The first `remainder` participants, ordered by user id, get `base + 1`; the rest get `base`. Shares always sum exactly to the amount.
  - Example: $10.00 among 3 = 334, 333, 333 cents.
- Maximum single expense: $100,000.00 (10,000,000 cents).

### 5.2 Balances

Computed from records every time, never stored.

For each ordered pair (A, B):

```
owed(A -> B) = sum of A's shares in expenses B paid
             - sum of B's shares in expenses A paid
             - settlements A paid B
             + settlements B paid A
```

If the result is positive, "A owes B" that amount. If negative, flip it to "B owes A". If zero, show nothing. A payer's own share creates no debt.

Net balance for a user = total they are owed minus total they owe. Sum of all net balances in a household is always 0.

### 5.3 Access

- Every household request checks membership on the server. Non-members get 404 (do not reveal that the household exists).
- Payer, participants, settlement parties, and chore assignees must all be members of that household.
- Edit/delete: creator of the record or the household owner. Others get 403.

## 6. Data model

| Table | Columns | Constraints |
|-------|---------|-------------|
| users | id, email, password_hash, display_name, created_at | email unique, stored lowercase |
| households | id, name, invite_code, created_by -> users, created_at | invite_code unique |
| memberships | id, user_id -> users, household_id -> households, role, joined_at | unique (user_id, household_id); role in (owner, member) |
| expenses | id, household_id, payer_id -> users, description, amount_cents, date, created_by -> users, created_at, updated_at | amount_cents > 0 |
| expense_shares | id, expense_id -> expenses, user_id -> users, share_cents | unique (expense_id, user_id); share_cents >= 0; deleted with expense; sum = expense amount |
| settlements | id, household_id, from_user_id -> users, to_user_id -> users, amount_cents, date, note, created_by -> users, created_at | amount_cents > 0; from_user_id != to_user_id |
| chores | id, household_id, title, assignee_id -> users, due_date, completed_at (null = open), created_by -> users, created_at | |

```
users 1--* memberships *--1 households
households 1--* expenses 1--* expense_shares *--1 users
households 1--* settlements (from_user, to_user -> users)
households 1--* chores (assignee -> users)
```

## 7. API contracts

JSON over HTTP. All paths start with `/api`. Auth uses a session cookie set at login.

Conventions:

- Money fields end in `_cents` and are integers. Dates are `YYYY-MM-DD`. Timestamps are ISO 8601 UTC.
- Errors: `{"error": "human readable message"}` with status 400 (validation), 401 (not logged in), 403 (not allowed), 404 (not found / not a member), 409 (conflict, e.g. email taken).
- Every `/api/households/:hid/...` route requires login and membership.

Shared object shapes:

```json
User:       {"id": 1, "email": "a@b.com", "display_name": "George"}
Household:  {"id": 1, "name": "727 Apt", "invite_code": "K7Q2M9XP", "role": "owner",
             "members": [{"id": 1, "display_name": "George", "role": "owner"}]}
Expense:    {"id": 1, "description": "Groceries", "amount_cents": 6000, "date": "2026-11-11",
             "payer_id": 1, "created_by": 1,
             "shares": [{"user_id": 1, "share_cents": 2000}, {"user_id": 2, "share_cents": 2000}]}
Settlement: {"id": 1, "from_user_id": 2, "to_user_id": 1, "amount_cents": 2000,
             "date": "2026-11-12", "note": "venmo", "created_by": 2}
Chore:      {"id": 1, "title": "Take out trash", "assignee_id": 3, "due_date": "2026-11-14",
             "completed_at": null, "created_by": 1}
```

### Auth (George)

| Method | Path | Body | Success |
|--------|------|------|---------|
| POST | `/api/auth/register` | `{email, display_name, password}` | 201 User, logged in |
| POST | `/api/auth/login` | `{email, password}` | 200 User |
| POST | `/api/auth/logout` | | 204 |
| GET | `/api/auth/me` | | 200 User, or 401 |

### Households (George)

| Method | Path | Body | Success |
|--------|------|------|---------|
| GET | `/api/households` | | 200 `[Household]` (mine) |
| POST | `/api/households` | `{name}` | 201 Household |
| POST | `/api/households/join` | `{invite_code}` | 200 Household; 404 bad code |
| GET | `/api/households/:hid` | | 200 Household |

### Expenses (Nebraas)

| Method | Path | Body | Success |
|--------|------|------|---------|
| GET | `/api/households/:hid/expenses` | | 200 `[Expense]` newest first |
| POST | `/api/households/:hid/expenses` | `{description, amount_cents, date, payer_id, participant_ids}` | 201 Expense |
| PUT | `/api/households/:hid/expenses/:eid` | same as POST | 200 Expense |
| DELETE | `/api/households/:hid/expenses/:eid` | | 204 |

### Balances and settlements (Nebraas)

| Method | Path | Body | Success |
|--------|------|------|---------|
| GET | `/api/households/:hid/balances` | | 200 `{"debts": [{"from_user_id", "to_user_id", "amount_cents"}], "net": [{"user_id", "net_cents"}]}` |
| GET | `/api/households/:hid/settlements` | | 200 `[Settlement]` newest first |
| POST | `/api/households/:hid/settlements` | `{from_user_id, to_user_id, amount_cents, date, note?}` | 201 Settlement |
| DELETE | `/api/households/:hid/settlements/:sid` | | 204 |

### Chores (Anusha)

| Method | Path | Body | Success |
|--------|------|------|---------|
| GET | `/api/households/:hid/chores?status=open\|done` | | 200 `[Chore]` by due date |
| POST | `/api/households/:hid/chores` | `{title, assignee_id, due_date}` | 201 Chore |
| PATCH | `/api/households/:hid/chores/:cid` | any of `{title, assignee_id, due_date, completed}` | 200 Chore |
| DELETE | `/api/households/:hid/chores/:cid` | | 204 |

The dashboard (F5) is built on the client from the balances, chores, and expenses endpoints. No separate dashboard endpoint.

## 8. Non-functional requirements

- **Security**: hashed passwords; HTTP-only session cookie; all permission checks on the server; no secrets committed to the repo.
- **Correctness**: money math covered by automated tests (rounding, edits, deletes, partial settlements, the worked example).
- **Privacy**: tests confirm a user in household A cannot read or change anything in household B.
- **Usability**: works on desktop and phone-width browsers.
- **Deployment**: publicly reachable URL with a persistent database.

## 9. Testing plan

- Unit tests: equal split (even, remainder, single participant, payer not a participant); pairwise balance calculation.
- API tests: each endpoint's success path, validation errors, 401, 403, 404 for non-members.
- Multi-account manual test: three accounts in one household plus one outsider account, run the worked example end to end.
- Mobile check of every screen at 360px width.

## 10. Open questions for the team

- Tech stack: the proposal slides list React + TypeScript, Python + Flask, and PostgreSQL + SQLAlchemy. Confirm before Milestone 2.
- Hosting provider for deployment.
- Should settlements be allowed to exceed the current debt (creating a reverse debt)? Current spec: no.
