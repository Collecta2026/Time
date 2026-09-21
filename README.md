# Time — HR & Payroll (Egypt)

A bilingual (English / العربية) HR and payroll system built for companies operating
under Egyptian labour law. Same stack as your Collecta build: a single Flask app,
SQLite locally and Postgres (Neon) in production, deployed on Render.

## What it does

- **Employees** — full records, start/end dates, contract type, bank details, medical enrolment.
- **Grades & spine points** — a grading scale where each spine point carries a salary, so every
  employee sits on a point with visible room to grow to the points above.
- **Attendance** — imported from your external fingerprint system by CSV. Overtime and
  shortfall are worked out per day against the standard working hours.
- **Leave** — annual, sick, casual, maternity, unpaid, with paid percentage.
- **Loans** — principal, monthly deduction and outstanding balance; deductions are applied
  automatically when a payroll run is finalised.
- **Medical benefits** — plans with employer and employee monthly shares.
- **Payroll** — full monthly payroll: gross, overtime, **social insurance**, **income tax**,
  loan and absence deductions, net pay, and printable **payslips** — run through a
  **scheme-of-delegation approval workflow** (below).
- **Payment schedule** — a printable schedule for Finance showing each employee's net pay with
  bank and account, the total to disburse, and the statutory remittances to the Tax Authority
  and NOSI. Exports to Excel as a bank payment file.
- **Contracts** — a printable **Arabic** employment contract (a legal requirement under
  Law 14/2025), populated from the employee record.
- **Reports** — attendance, sick days, starters & leavers, management statistics, the **insurance
  remittance register** (every month's NOSI return for the year, each linking to its auditable
  schedule), the **leave-pay provision** (tracked monthly), and the loan register. Each exports to
  Excel. An in-app **Help** guide is built in, and the full illustrated manual is supplied as
  `docs/Time_Installation_and_User_Manual.docx` (step-by-step install is also in `INSTALL.md`).

## Roles and the payroll approval workflow

Payroll follows the same maker-checker scheme of delegation as the cash-cycle system, with an
append-only **audit log** of every action:

```
  HR prepares  ─►  Finance Manager approves  ─►  Managing Director authorises  ─►  paid
   (draft →          (prepared → approved,          (approved → authorised,         (marked
    prepared)         segregation of duties          joint release; loan             paid by
                      enforced)                      balances reduced here)          Finance)
```

Roles (set per user under **Users**, admin only):

- **admin** — full control, user administration and settings.
- **hr** — prepares payroll and manages people, attendance, leave and loans.
- **finance_manager** — approves payroll, sees all finance information, prints the payment
  schedule, marks runs paid, and can view the audit log.
- **md** — the joint authorisation (final release) of payroll for payment.
- **viewer** — read-only.

The **scheme of delegation is data**, not code: in Settings you set net-total bands and, for
each band, whether Finance Manager approval alone is enough or a joint MD release is also
required. The default band requires both on every payroll. Segregation of duties is enforced —
the person who prepared a run cannot approve it.

When SEED_DEMO is on, demo logins are created for each role
(`hr@time.eg`, `finance@time.eg`, `md@time.eg`, all `Time2026`) so the workflow is
demonstrable out of the box.

## The statutory engine

All rates live in **Settings** so an administrator keeps the system compliant without a code
change. The figures shipped as defaults reflect the position for 2026:

- **Social insurance (Law 148/2019):** employee 11%, employer 18.75%, emergency fund 1%,
  on the insurable wage between the floor (EGP 2,700) and ceiling (EGP 16,700). *Both limits
  rise 15% every January — update them in Settings each year.*
- **Income tax (Law 91/2005, amended by Law 7/2024):** seven progressive bands 0%–27.5% with
  the six-column bracket-integration table, the EGP 20,000 annual salary exemption, and the
  employee's social insurance deducted before tax.
- **Working time & overtime (Law 14/2025):** 8 hours/day, 48/week; overtime 35% day / 70%
  night or rest-day.

The calculations are in `payroll.py` and are independently unit-testable.

## Run locally

```bash
pip install -r requirements.txt
python app.py           # http://localhost:5000
```

A demo company (Scientific Gate Co.) with departments, grades, twelve employees, loans and a
month of attendance is seeded on first run. Sign in with **admin@time.eg / Time2026**.

## Deploy — GitHub → Render → Neon

1. **Neon** — create a project in the **London** region, copy the connection string
   (the `postgresql://...` pooled URL).
2. **GitHub** — push this folder to a new repository.
3. **Render** — New → **Blueprint**, point it at the repo. `render.yaml` is picked up
   automatically. When prompted, set:
   - `DATABASE_URL` → your Neon connection string
   - `ADMIN_EMAIL` and `ADMIN_PASSWORD` → your own admin login
   - `SEED_DEMO` → `true` for the first deploy if you want the demo data, then change it back
     to `false` and redeploy.
   `SECRET_KEY` is generated for you.
4. Tables are created automatically on first boot and the admin user is made from your env vars.
5. Add your custom domain under the Render service's **Settings → Custom Domains**.

## Attendance import format

A CSV with a header row. Either give hours directly, or in/out times and the app computes them:

```
employee_code,date,hours_worked,time_in,time_out
1001,2026-01-04,8,,
1002,2026-01-04,,08:30,17:00
```

`employee_code` must match the code on the employee record (set this to the worker's
fingerprint ID). Download a ready template from the Attendance page.

## A note on compliance and configuration

Every key parameter is set in **Settings** and can be changed at setup and at any time
afterwards — the insurance rates, floor and ceiling, the tax exemption, working hours and
overtime premiums, leave policy, the paying-bank details and the scheme-of-delegation bands.
This is how you keep the system current: confirm the insurable-wage ceiling each January (it
rises 15%), and adjust rates whenever the law changes, without a code change.

Time implements the rules as published, but tax and insurance figures move. Treat the seeded
defaults as a starting point and have payroll output checked before first live use.
