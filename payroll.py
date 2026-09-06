"""
Egyptian statutory payroll engine for "Time".

All rates and thresholds are passed in from CompanySettings so the product can be
kept compliant by an administrator without a code change (the law revises the
insurance ceilings every January). The defaults seeded in the database reflect
the position for 2026:

  Social Insurance & Pensions Law No. 148 of 2019
    - Employee contribution ....... 11.00%  of the insurable wage
    - Employer contribution ....... 18.75%  of the insurable wage
    - Emergency / labour fund ......  1.00%  of the insurable wage (employer only)
    - Insurable wage floor ......... EGP 2,700 / month  (2026)
    - Insurable wage ceiling ....... EGP 16,700 / month (2026)
    - Both limits rise 15% every 1 January (2021-2028).

  Income Tax Law No. 91 of 2005 (as amended by Law No. 7 of 2024)
    - Seven progressive bands, 0% .. 27.5%
    - Annual personal salary exemption ... EGP 20,000
    - The employee's social-insurance contribution is deductible before tax.
    - Lower bands are progressively withdrawn for higher total incomes
      (the six-column "bracket integration" table) -- implemented below.

  Labour Law No. 14 of 2025
    - Standard time .... 8 hours/day or 48 hours/week
    - Overtime premium . 35% (daytime) / 70% (night or rest-day)

Everything is computed in EGP and rounded to 2 decimals at the boundaries.
"""

from decimal import Decimal, ROUND_HALF_UP

TWOPLACES = Decimal("0.01")


def _d(x):
    return Decimal(str(x or 0))


def _round(x):
    return _d(x).quantize(TWOPLACES, rounding=ROUND_HALF_UP)


# --------------------------------------------------------------------------- #
#  Social insurance
# --------------------------------------------------------------------------- #
def insurable_wage(total_monthly_wage, floor, ceiling):
    """Clamp the employee's monthly wage into the statutory insurable band."""
    w = _d(total_monthly_wage)
    lo, hi = _d(floor), _d(ceiling)
    if w < lo:
        w = lo
    if w > hi:
        w = hi
    return _round(w)


def social_insurance(insurable, s):
    """Return the monthly social-insurance figures for a given insurable wage."""
    base = _d(insurable)
    emp = _round(base * _d(s.si_employee_pct) / 100)
    er = _round(base * _d(s.si_employer_pct) / 100)
    fund = _round(base * _d(s.emergency_fund_pct) / 100)
    return {
        "insurable_wage": _round(base),
        "employee": emp,          # deducted from the employee
        "employer": er,           # employer cost
        "emergency_fund": fund,   # employer cost
        "employer_total": _round(er + fund),
    }


# --------------------------------------------------------------------------- #
#  Income tax (annual, then / 12) -- the Egyptian bracket-integration table
# --------------------------------------------------------------------------- #
def _bands_for_total(total):
    """
    Return the list of (upper_limit, rate) bands that apply to a given total
    annual taxable income. Egypt withdraws the lower-rate bands as income rises.
    upper_limit is the top of the band in EGP; the final band uses None.
    """
    t = _d(total)
    if t <= 600000:
        return [(40000, 0), (55000, 10), (70000, 15),
                (200000, 20), (400000, 22.5), (None, 25)]
    if t <= 700000:
        return [(55000, 10), (70000, 15), (200000, 20),
                (400000, 22.5), (None, 25)]
    if t <= 800000:
        return [(70000, 15), (200000, 20), (400000, 22.5), (None, 25)]
    if t <= 900000:
        return [(200000, 20), (400000, 22.5), (None, 25)]
    if t <= 1200000:
        return [(400000, 22.5), (None, 25)]
    return [(1200000, 25), (None, 27.5)]


def annual_income_tax(taxable_annual):
    """Progressive tax on an annual taxable income, applying band integration."""
    taxable = _d(taxable_annual)
    if taxable <= 0:
        return Decimal("0.00")
    bands = _bands_for_total(taxable)
    tax = Decimal("0")
    lower = Decimal("0")
    for upper, rate in bands:
        cap = taxable if upper is None else min(taxable, _d(upper))
        if cap > lower:
            tax += (cap - lower) * _d(rate) / 100
        lower = _d(upper) if upper is not None else taxable
        if upper is not None and taxable <= _d(upper):
            break
    return _round(tax)


def monthly_income_tax(monthly_taxable_gross, monthly_employee_si, s):
    """
    Annualise the monthly taxable pay, remove the personal exemption and the
    (tax-deductible) employee social-insurance contribution, tax it, divide by 12.
    """
    annual_gross = _d(monthly_taxable_gross) * 12
    annual_si = _d(monthly_employee_si) * 12
    exemption = _d(s.tax_annual_exemption)
    taxable = annual_gross - annual_si - exemption
    if taxable < 0:
        taxable = Decimal("0")
    return _round(annual_income_tax(taxable) / 12)


# --------------------------------------------------------------------------- #
#  Time-based earnings and deductions
# --------------------------------------------------------------------------- #
def hourly_rate(monthly_salary, s):
    """Daily rate = monthly / days_per_month; hourly = daily / standard daily hours."""
    daily = _d(monthly_salary) / _d(s.days_per_month or 30)
    return daily / _d(s.standard_daily_hours or 8)


def overtime_pay(monthly_salary, ot_day_hours, ot_night_hours, s):
    hr = hourly_rate(monthly_salary, s)
    day = hr * _d(ot_day_hours) * (1 + _d(s.overtime_day_pct) / 100)
    night = hr * _d(ot_night_hours) * (1 + _d(s.overtime_night_pct) / 100)
    return _round(day + night)


def absence_deduction(monthly_salary, hours_short, s):
    return _round(hourly_rate(monthly_salary, s) * _d(hours_short))


# --------------------------------------------------------------------------- #
#  Full monthly payslip
# --------------------------------------------------------------------------- #
def compute_payslip(*, basic, allowances, ot_day_hours, ot_night_hours,
                    hours_short, loan_deduction, other_deductions,
                    insurable_override, s):
    """
    Build a complete monthly payslip breakdown. All money inputs are monthly EGP.
    `s` is the CompanySettings row. Returns a dict of Decimals.
    """
    basic = _d(basic)
    allowances = _d(allowances)
    ot = overtime_pay(basic + allowances, ot_day_hours, ot_night_hours, s)
    gross = _round(basic + allowances + ot)

    iw = _d(insurable_override) if insurable_override else \
        insurable_wage(basic + allowances, s.si_floor, s.si_ceiling)
    si = social_insurance(iw, s)

    tax = monthly_income_tax(gross, si["employee"], s)
    absence = absence_deduction(basic + allowances, hours_short, s)
    loan = _round(loan_deduction)
    other = _round(other_deductions)

    total_deductions = _round(si["employee"] + tax + absence + loan + other)
    net = _round(gross - total_deductions)

    return {
        "basic": _round(basic),
        "allowances": _round(allowances),
        "overtime": ot,
        "gross": gross,
        "insurable_wage": si["insurable_wage"],
        "si_employee": si["employee"],
        "si_employer": si["employer"],
        "emergency_fund": si["emergency_fund"],
        "employer_cost": _round(gross + si["employer_total"]),
        "income_tax": tax,
        "absence_deduction": absence,
        "loan_deduction": loan,
        "other_deductions": other,
        "total_deductions": total_deductions,
        "net_pay": net,
    }
