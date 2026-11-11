# SplitSpace - Wireframes

Low-fidelity layouts for the 8 screens in `specifications.md` section 4. Desktop width shown; on phones (360px) side-by-side panels stack vertically.

## Shared header (all logged-in screens)

```
+------------------------------------------------------------+
| SplitSpace     727 Apt v        Dashboard Expenses ...  [Log out] |
+------------------------------------------------------------+
```

`727 Apt v` switches between my households. Nav links: Dashboard, Expenses, Balances, Chores, Members.

## 1. Login `/login`

```
+-------------------------------+
|          SplitSpace           |
|                               |
|  Email     [_______________]  |
|  Password  [_______________]  |
|                               |
|           [ Log in ]          |
|                               |
|  No account? Register         |
+-------------------------------+
```

## 2. Register `/register`

```
+-------------------------------+
|       Create an account       |
|                               |
|  Email         [___________]  |
|  Display name  [___________]  |
|  Password      [___________]  |
|  (at least 8 characters)      |
|                               |
|         [ Register ]          |
|                               |
|  Have an account? Log in      |
+-------------------------------+
```

## 3. My households `/households`

```
+------------------------------------------------------------+
| My households                                              |
|                                                            |
|  727 Apt               3 members   owner        [ Open ]   |
|  Summer sublet         2 members   member       [ Open ]   |
|                                                            |
| +-------------------------+  +---------------------------+ |
| | Create a household      |  | Join with invite code     | |
| | Name [_______________]  |  | Code [________]           | |
| |          [ Create ]     |  |          [ Join ]         | |
| +-------------------------+  +---------------------------+ |
+------------------------------------------------------------+
```

No households yet: the list is replaced by "Create or join a household to get started."

## 4. Dashboard `/households/:id`

```
+------------------------------------------------------------+
| [header]                                                   |
|                                                            |
| +------------------------+  +----------------------------+ |
| | My balance             |  | My chores                  | |
| |  You owe $20.00        |  | ! Trash        due Nov 10  | |  <- overdue, highlighted
| |                        |  | [ ] Dishes     due Nov 12  | |
| |  You owe Nebraas $20   |  | [ ] Vacuum     due Nov 15  | |
| |   [ Record payment ]   |  |          View all chores > | |
| +------------------------+  +----------------------------+ |
|                                                            |
| Recent expenses                                            |
|  Nov 11  Groceries     $60.00  paid by Nebraas            |
|  Nov 09  Paper towels  $12.00  paid by Anusha             |
|  ... (5 max)                          View all expenses >  |
+------------------------------------------------------------+
```

## 5. Expenses `/households/:id/expenses`

```
+------------------------------------------------------------+
| [header]                                                   |
| Expenses                                  [ + Add expense ]|
|                                                            |
|  Nov 11  Groceries        $60.00   paid by Nebraas  [Edit] |
|          Nebraas $20.00 / George $20.00 / Anusha $20.00    |
|  Nov 09  Paper towels     $12.00   paid by Anusha   [Edit] |
|          Anusha $6.00 / George $6.00                       |
+------------------------------------------------------------+

Add / edit expense (panel or modal)
+-------------------------------+
| Description [_______________] |
| Amount   $  [_______]         |
| Date        [2026-11-11]      |
| Paid by     [Nebraas v]       |
| Split between                 |
|   [x] Nebraas                 |
|   [x] George                  |
|   [x] Anusha                  |
| Each pays: $20.00             |  <- live preview of equal split
|                               |
| [Delete]     [Cancel] [Save]  |  <- Delete only when editing
+-------------------------------+
```

Edit and Delete only appear for the creator or the owner.

## 6. Balances `/households/:id/balances`

```
+------------------------------------------------------------+
| [header]                                                   |
| Who owes whom                                              |
|  George owes Nebraas    $20.00          [ Record payment ] |
|  Anusha owes Nebraas    $20.00          [ Record payment ] |
|                                                            |
|  (Everyone is settled up.)   <- when list is empty         |
|                                                            |
| Payment history                                            |
|  Nov 12  George paid Nebraas  $20.00  "venmo"     [Delete] |
+------------------------------------------------------------+

Record payment (prefilled from the row clicked)
+-------------------------------+
| From    [George v]            |
| To      [Nebraas v]           |
| Amount  $ [20.00]  (max $20)  |
| Date    [2026-11-12]          |
| Note    [_______________]     |
|          [Cancel] [Save]      |
+-------------------------------+
```

## 7. Chores `/households/:id/chores`

```
+------------------------------------------------------------+
| [header]                                                   |
| Chores          ( Open ) ( Done )            [ + Add chore ]|
|                                                            |
|  [ ] ! Take out trash   Anusha    due Nov 10  OVERDUE [Edit]|
|  [ ]   Dishes           George    due Nov 12          [Edit]|
|  [ ]   Vacuum           Nebraas   due Nov 15          [Edit]|
+------------------------------------------------------------+

Add / edit chore
+-------------------------------+
| Title     [_______________]   |
| Assignee  [George v]          |
| Due date  [2026-11-14]        |
| [Delete]    [Cancel] [Save]   |
+-------------------------------+
```

Checking the box marks the chore done and moves it to the Done tab. Unchecking on the Done tab reopens it.

## 8. Members `/households/:id/members`

```
+------------------------------------------------------------+
| [header]                                                   |
| 727 Apt - members                                          |
|  Nebraas Sattar     owner                                  |
|  George Ji          member                                 |
|  Anusha Prabhakar   member                                 |
|                                                            |
| Invite roommates                                           |
|  Code:  K7Q2M9XP   [ Copy ]                                |
|  Share this code. They join from "My households".          |
+------------------------------------------------------------+
```
