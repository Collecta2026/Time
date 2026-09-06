from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


# --------------------------------------------------------------------------- #
#  Access control
# --------------------------------------------------------------------------- #
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(160), unique=True, nullable=False)
    name = db.Column(db.String(160))
    role = db.Column(db.String(20), default="admin")
    # roles: admin | hr | finance_manager | md | viewer
    #   admin           full control + user administration + settings
    #   hr              prepares payroll, manages people/attendance/leave/loans
    #   finance_manager approves payroll, views all finance info, prints schedules
    #   md              joint authorisation (final release) of payroll for payment
    #   viewer          read-only
    pw_hash = db.Column(db.String(255))
    active = db.Column(db.Boolean, default=True)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, pw):
        self.pw_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.pw_hash, pw)

    def has_role(self, *roles):
        return self.role == "admin" or self.role in roles


# --------------------------------------------------------------------------- #
#  Company-wide configuration (single tenant per deployment)
# --------------------------------------------------------------------------- #
class CompanySettings(db.Model):
    __tablename__ = "settings"
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(200), default="Your Company")
    company_name_ar = db.Column(db.String(200), default="")
    address = db.Column(db.String(300), default="")
    tax_id = db.Column(db.String(60), default="")
    insurance_no = db.Column(db.String(60), default="")
    currency = db.Column(db.String(8), default="EGP")

    # Paying bank (used on the finance payment schedule)
    pay_bank_name = db.Column(db.String(120), default="")
    pay_bank_account = db.Column(db.String(60), default="")

    # Working time
    standard_daily_hours = db.Column(db.Float, default=8)
    standard_weekly_hours = db.Column(db.Float, default=48)
    working_days = db.Column(db.String(40), default="SU,MO,TU,WE,TH")  # rest Fri/Sat
    days_per_month = db.Column(db.Integer, default=30)

    # Social insurance (Law 148/2019 — 2026 defaults)
    si_employee_pct = db.Column(db.Float, default=11.0)
    si_employer_pct = db.Column(db.Float, default=18.75)
    emergency_fund_pct = db.Column(db.Float, default=1.0)
    si_floor = db.Column(db.Float, default=2700)
    si_ceiling = db.Column(db.Float, default=16700)

    # Income tax (Law 91/2005 as amended)
    tax_annual_exemption = db.Column(db.Float, default=20000)

    # Overtime premium (Law 14/2025)
    overtime_day_pct = db.Column(db.Float, default=35.0)
    overtime_night_pct = db.Column(db.Float, default=70.0)

    # Leave policy (days) — configurable defaults from Law 14/2025
    annual_leave_y1 = db.Column(db.Integer, default=15)
    annual_leave_std = db.Column(db.Integer, default=21)
    annual_leave_senior = db.Column(db.Integer, default=30)
    casual_leave = db.Column(db.Integer, default=7)
    probation_months = db.Column(db.Integer, default=3)

    updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def get():
        s = CompanySettings.query.first()
        if not s:
            s = CompanySettings()
            db.session.add(s)
            db.session.commit()
        return s


# --------------------------------------------------------------------------- #
#  Organisation structure and grading
# --------------------------------------------------------------------------- #
class Department(db.Model):
    __tablename__ = "departments"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    name_ar = db.Column(db.String(120), default="")
    employees = db.relationship("Employee", backref="department", lazy=True)


class Grade(db.Model):
    __tablename__ = "grades"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False)         # e.g. G1
    name = db.Column(db.String(120), nullable=False)
    name_ar = db.Column(db.String(120), default="")
    order = db.Column(db.Integer, default=0)
    points = db.relationship("SpinePoint", backref="grade", lazy=True,
                             order_by="SpinePoint.point_no",
                             cascade="all, delete-orphan")


class SpinePoint(db.Model):
    __tablename__ = "spine_points"
    id = db.Column(db.Integer, primary_key=True)
    grade_id = db.Column(db.Integer, db.ForeignKey("grades.id"), nullable=False)
    point_no = db.Column(db.Integer, nullable=False)         # spine point number
    monthly_salary = db.Column(db.Float, nullable=False)     # EGP / month


# --------------------------------------------------------------------------- #
#  Employees
# --------------------------------------------------------------------------- #
class Employee(db.Model):
    __tablename__ = "employees"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), unique=True, nullable=False)  # matches fingerprint id
    name = db.Column(db.String(200), nullable=False)
    name_ar = db.Column(db.String(200), default="")
    national_id = db.Column(db.String(20), default="")
    gender = db.Column(db.String(10), default="")            # male | female
    dob = db.Column(db.Date)
    phone = db.Column(db.String(40), default="")
    email = db.Column(db.String(160), default="")
    address = db.Column(db.String(300), default="")

    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"))
    job_title = db.Column(db.String(160), default="")
    job_title_ar = db.Column(db.String(160), default="")
    grade_id = db.Column(db.Integer, db.ForeignKey("grades.id"))
    spine_point = db.Column(db.Integer)

    hire_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(20), default="active")      # active | left
    contract_type = db.Column(db.String(30), default="indefinite")  # indefinite|fixed|probation

    # Pay
    basic_salary = db.Column(db.Float, default=0)            # monthly EGP
    allowances = db.Column(db.Float, default=0)              # monthly EGP
    insurable_wage = db.Column(db.Float)                     # override; else clamp of basic+allow

    # Banking
    bank_name = db.Column(db.String(120), default="")
    bank_account = db.Column(db.String(60), default="")

    # Medical / benefits enrolment
    benefit_id = db.Column(db.Integer, db.ForeignKey("benefit_plans.id"))

    created = db.Column(db.DateTime, default=datetime.utcnow)

    grade = db.relationship("Grade")
    loans = db.relationship("Loan", backref="employee", lazy=True)

    @property
    def total_monthly(self):
        return (self.basic_salary or 0) + (self.allowances or 0)

    @property
    def years_service(self):
        if not self.hire_date:
            return 0
        end = self.end_date or date.today()
        return round((end - self.hire_date).days / 365.25, 1)

    def active_loans(self):
        return [l for l in self.loans if l.status == "active"]


# --------------------------------------------------------------------------- #
#  Medical / benefits
# --------------------------------------------------------------------------- #
class BenefitPlan(db.Model):
    __tablename__ = "benefit_plans"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    name_ar = db.Column(db.String(160), default="")
    provider = db.Column(db.String(160), default="")
    employer_cost = db.Column(db.Float, default=0)   # monthly EGP per head
    employee_cost = db.Column(db.Float, default=0)   # monthly EGP deducted
    coverage = db.Column(db.String(300), default="")
    active = db.Column(db.Boolean, default=True)
    members = db.relationship("Employee", backref="benefit", lazy=True)


# --------------------------------------------------------------------------- #
#  Loans
# --------------------------------------------------------------------------- #
class Loan(db.Model):
    __tablename__ = "loans"
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    issue_date = db.Column(db.Date, default=date.today)
    principal = db.Column(db.Float, nullable=False)
    monthly_deduction = db.Column(db.Float, nullable=False)
    outstanding = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(200), default="")
    status = db.Column(db.String(20), default="active")   # active | settled
    payments = db.relationship("LoanPayment", backref="loan", lazy=True,
                               cascade="all, delete-orphan")


class LoanPayment(db.Model):
    __tablename__ = "loan_payments"
    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey("loans.id"), nullable=False)
    pay_date = db.Column(db.Date, default=date.today)
    amount = db.Column(db.Float, nullable=False)
    note = db.Column(db.String(120), default="")


# --------------------------------------------------------------------------- #
#  Attendance (fed from external fingerprint system)
# --------------------------------------------------------------------------- #
class Attendance(db.Model):
    __tablename__ = "attendance"
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    work_date = db.Column(db.Date, nullable=False)
    hours_worked = db.Column(db.Float, default=0)
    expected_hours = db.Column(db.Float, default=0)
    ot_day_hours = db.Column(db.Float, default=0)
    ot_night_hours = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default="present")  # present|absent|leave|holiday
    source = db.Column(db.String(20), default="import")
    employee = db.relationship("Employee")
    __table_args__ = (db.UniqueConstraint("employee_id", "work_date",
                                          name="uq_att_emp_date"),)


# --------------------------------------------------------------------------- #
#  Leave
# --------------------------------------------------------------------------- #
class Leave(db.Model):
    __tablename__ = "leaves"
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    leave_type = db.Column(db.String(30), nullable=False)  # annual|sick|casual|maternity|unpaid
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    days = db.Column(db.Float, default=0)
    paid_pct = db.Column(db.Float, default=100)
    note = db.Column(db.String(200), default="")
    status = db.Column(db.String(20), default="approved")
    employee = db.relationship("Employee")


# --------------------------------------------------------------------------- #
#  Payroll
# --------------------------------------------------------------------------- #
class PayrollRun(db.Model):
    __tablename__ = "payroll_runs"
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    # workflow: draft -> prepared -> approved -> authorised -> paid
    status = db.Column(db.String(20), default="draft")
    created = db.Column(db.DateTime, default=datetime.utcnow)

    # scheme-of-delegation trail (name snapshots kept for permanence)
    prepared_by = db.Column(db.String(160))
    prepared_at = db.Column(db.DateTime)
    approved_by = db.Column(db.String(160))       # Finance Manager
    approved_at = db.Column(db.DateTime)
    authorised_by = db.Column(db.String(160))     # Managing Director (joint release)
    authorised_at = db.Column(db.DateTime)
    paid_by = db.Column(db.String(160))
    paid_at = db.Column(db.DateTime)
    reject_reason = db.Column(db.String(300))

    payslips = db.relationship("Payslip", backref="run", lazy=True,
                               cascade="all, delete-orphan")
    __table_args__ = (db.UniqueConstraint("year", "month", name="uq_run_period"),)

    @property
    def period_label(self):
        return f"{self.year}-{self.month:02d}"

    @property
    def locked(self):
        """Draft is the only editable/recomputable state."""
        return self.status != "draft"

    @property
    def net_total(self):
        return sum(p.net_pay for p in self.payslips)


class Payslip(db.Model):
    __tablename__ = "payslips"
    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.Integer, db.ForeignKey("payroll_runs.id"), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)

    basic = db.Column(db.Float, default=0)
    allowances = db.Column(db.Float, default=0)
    overtime = db.Column(db.Float, default=0)
    gross = db.Column(db.Float, default=0)

    insurable_wage = db.Column(db.Float, default=0)
    si_employee = db.Column(db.Float, default=0)
    si_employer = db.Column(db.Float, default=0)
    emergency_fund = db.Column(db.Float, default=0)

    income_tax = db.Column(db.Float, default=0)
    absence_deduction = db.Column(db.Float, default=0)
    loan_deduction = db.Column(db.Float, default=0)
    other_deductions = db.Column(db.Float, default=0)

    total_deductions = db.Column(db.Float, default=0)
    net_pay = db.Column(db.Float, default=0)
    employer_cost = db.Column(db.Float, default=0)

    hours_worked = db.Column(db.Float, default=0)
    hours_expected = db.Column(db.Float, default=0)

    employee = db.relationship("Employee")


# --------------------------------------------------------------------------- #
#  Scheme of delegation (delegation-as-data) + append-only audit log
# --------------------------------------------------------------------------- #
class DelegationBand(db.Model):
    """
    Payroll authorisation bands by net total. The band that contains a run's net
    total decides which sign-offs are required. Mirrors the cash-cycle scheme of
    delegation: Finance Manager approval, with a joint MD release above a limit.
    """
    __tablename__ = "delegation_bands"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    min_amount = db.Column(db.Float, default=0)
    max_amount = db.Column(db.Float)              # null = no upper limit
    requires_fm = db.Column(db.Boolean, default=True)
    requires_md = db.Column(db.Boolean, default=True)
    order = db.Column(db.Integer, default=0)


class AuditLog(db.Model):
    """Append-only record of who did what, when."""
    __tablename__ = "audit_log"
    id = db.Column(db.Integer, primary_key=True)
    ts = db.Column(db.DateTime, default=datetime.utcnow)
    actor = db.Column(db.String(160))
    action = db.Column(db.String(60))
    target = db.Column(db.String(120))
    detail = db.Column(db.String(300))


# --------------------------------------------------------------------------- #
#  Statutory leave-pay provision (monthly snapshot, tracked for finance)
# --------------------------------------------------------------------------- #
class LeaveProvision(db.Model):
    """
    A posted monthly snapshot of each employee's accrued-but-untaken statutory
    annual leave and its monetary value (the leave liability finance carries).
    Posting a month writes one row per active employee; re-posting replaces them.
    """
    __tablename__ = "leave_provision"
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    entitlement_days = db.Column(db.Float, default=0)   # annual statutory entitlement
    accrued_days = db.Column(db.Float, default=0)        # earned YTD to this month
    taken_days = db.Column(db.Float, default=0)          # annual leave taken YTD
    balance_days = db.Column(db.Float, default=0)        # accrued - taken
    daily_rate = db.Column(db.Float, default=0)
    provision_value = db.Column(db.Float, default=0)     # balance_days * daily_rate
    monthly_accrual = db.Column(db.Float, default=0)     # this month's charge
    posted_by = db.Column(db.String(160))
    created = db.Column(db.DateTime, default=datetime.utcnow)
    employee = db.relationship("Employee")
    __table_args__ = (db.UniqueConstraint("year", "month", "employee_id",
                                          name="uq_prov_period_emp"),)
