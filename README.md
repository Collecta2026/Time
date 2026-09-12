# Scientific Gate — Cash Flow Budgeting System

Release 1. A bilingual (English / العربية) weekly cash flow forecasting and
budgeting system for Scientific Gate Co., built on the same architecture as
Collecta: Flask + SQLAlchemy, Neon/Postgres in production, a role and
capability matrix enforced server-side, an approvals queue and a full audit
log.

## Running it locally

```bash
pip install -r requirements.txt
python run_app.py            # http://127.0.0.1:5000
```

The first page is a setup wizard: it creates the administrator, names the
organisation, sets the default language and can load a worked example so the
forecast is populated from the start.

With no `DATABASE_URL` set it uses a local SQLite file, so it runs on a laptop
with nothing else installed. Set `DATABASE_URL` to a Neon connection string for
the hosted deployment (see `.env.example`).

## What is in Release 1

**Ten independently editable tables**, each with its own page, its own fields,
its own filters and its own place in the scheme of delegation:

| Cash in | Cash out |
|---|---|
| Customer collections (instalments, down payments, advances, invoice settlements, retention releases — with customer number, contract and instalment number, and a weekly planner view) | Bank loan instalments |
| Ad hoc cash inflows | Supplier repayment instalments |
| One-off items (in or out) | Cheques payable (issue date, payable date, payee, cheque state) |
| | Customer refunds |
| | Petty cash replenishments (by employee) |
| | Fixed weekly costs |
| | Fixed monthly costs |

**Bank and cash accounts** in EGP and USD, each with a balance, an as-at date
and an overdraft limit, and a switch to include or exclude it from the forecast.

**Opening balances** roll forward automatically from the previous week's
closing balance, and any week can be pinned to an actual bank figure — the
override then rolls on from there.

**Dashboard** — the next six weeks (configurable) per currency with the EGP
equivalent, the lowest forecast balance, and shortage alerts both for a
negative balance and for falling below a set minimum buffer.

**Scheme of delegation** — eight roles, five actions per table (view, enter,
edit, delete, review & approve) plus thirteen core capabilities, all editable
in the app. Entries move draft → submitted → approved; only approved entries
count in the forecast unless the setting says otherwise, and nobody may
approve an entry they created themselves.

**Analysis** — revenue by type, cost elements as a percentage of total revenue
and of total cost, over any window of weeks.

**Rolling trend forecast** — takes the previous six completed weeks (configurable),
measures each revenue type and cost category week by week, and rolls it forward
by least-squares trend or flat average. It shows the weekly average, the trend
per week, the projection for the coming weeks, what is already booked in the
forward forecast, and the variance between the two — plus a projected cash
position running alongside the booked one. Recurring costs generate their own
historical occurrences, so a fixed weekly wage is measured even though no past
entry exists for it.

**Working week** — Sunday to Thursday by default, with Friday and Saturday
non-working and items on those days moving to the next working day. A
Saturday-to-Thursday preset (Friday off only) is available in settings if
Saturday is worked.

## Accuracy

The engine is covered by 54 tests in `tests/`, each asserting figures computed
independently of the code under test:

```bash
python -m pytest -q
```

The design decisions that protect accuracy are documented at the top of
`services.py`: weeks tile the calendar exactly, recurrences are generated as
nominal dates and only then shifted and placed, all money is `Decimal` with a
single rounding point, and the two currencies never mix.

## Still to come

* **Release 2** — CSV / Excel / PDF exports on every table and report, printable
  forecast and analysis packs, email alerts on forecast shortages.
* **Release 3** — Render / AWS Pro deployment pack, subdomain and SSL setup,
  operating manual and user training guide.
