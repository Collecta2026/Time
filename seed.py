"""Demo data so a fresh install is explorable. Skip in production: SEED_DEMO=false."""
from datetime import date, timedelta
import random
from models import (CompanySettings, Department, Grade, SpinePoint, Employee,
                    BenefitPlan, Loan, Attendance, Leave, User)


def run(db):
    # demo users covering the scheme of delegation
    for email, name, role in [("hr@time.eg", "Mona Adel (HR)", "hr"),
                              ("finance@time.eg", "Nadia Hassan (Finance Manager)", "finance_manager"),
                              ("md@time.eg", "Amr El-Bagoury (MD)", "md")]:
        if not User.query.filter_by(email=email).first():
            u = User(email=email, name=name, role=role)
            u.set_password("Time2026")
            db.session.add(u)

    s = CompanySettings.get()
    s.company_name = "Scientific Gate Co."
    s.company_name_ar = "شركة بوابة العلوم"
    s.address = "Nasr City, Cairo, Egypt"
    s.tax_id = "123-456-789"
    s.insurance_no = "SG-2011"
    s.pay_bank_name = "Commercial International Bank (CIB)"
    s.pay_bank_account = "EG•• •••• •••• •••• 1120"

    depts = {}
    for en, ar in [("Management", "الإدارة"), ("Finance", "المالية"),
                   ("Sales", "المبيعات"), ("Operations", "العمليات"),
                   ("Technical", "الفني"), ("HR", "الموارد البشرية")]:
        d = Department(name=en, name_ar=ar)
        db.session.add(d)
        depts[en] = d
    db.session.flush()

    grades = {}
    grade_defs = [
        ("G1", "Junior", "مبتدئ", 1, [(1, 6000), (2, 6600), (3, 7300), (4, 8000)]),
        ("G2", "Officer", "أخصائي", 2, [(1, 8500), (2, 9500), (3, 10500), (4, 11500)]),
        ("G3", "Senior", "أول", 3, [(1, 12500), (2, 14000), (3, 15500), (4, 17000)]),
        ("G4", "Manager", "مدير", 4, [(1, 19000), (2, 22000), (3, 25000), (4, 28000)]),
        ("G5", "Director", "مدير عام", 5, [(1, 32000), (2, 38000), (3, 45000)]),
    ]
    for code, name, name_ar, order, pts in grade_defs:
        g = Grade(code=code, name=name, name_ar=name_ar, order=order)
        db.session.add(g)
        db.session.flush()
        for pn, sal in pts:
            db.session.add(SpinePoint(grade_id=g.id, point_no=pn, monthly_salary=sal))
        grades[code] = g

    med = BenefitPlan(name="Standard medical cover", name_ar="تأمين طبي أساسي",
                      provider="MedNet Egypt", employer_cost=450, employee_cost=150,
                      coverage="Outpatient, inpatient, pharmacy — EGP 200k/yr limit")
    med_plus = BenefitPlan(name="Family medical cover", name_ar="تأمين طبي عائلي",
                           provider="MedNet Egypt", employer_cost=900, employee_cost=350,
                           coverage="Employee + dependants, dental & optical")
    db.session.add_all([med, med_plus])
    db.session.flush()

    people = [
        ("1001", "Amr El-Bagoury", "عمرو الباجوري", "male", "Management", "G5", 2, "Managing Director", "2011-06-01", med_plus),
        ("1002", "Nadia Hassan", "نادية حسن", "female", "Finance", "G4", 3, "Finance Manager", "2013-03-15", med_plus),
        ("1003", "Khaled Salah", "خالد صلاح", "male", "Finance", "G2", 4, "Credit Controller", "2016-09-01", med),
        ("1004", "Mona Adel", "منى عادل", "female", "HR", "G3", 2, "HR Business Partner", "2018-01-10", med),
        ("1005", "Tarek Fouad", "طارق فؤاد", "male", "Sales", "G3", 3, "Sales Lead", "2017-05-20", med),
        ("1006", "Sara Ibrahim", "سارة إبراهيم", "female", "Sales", "G2", 2, "Account Executive", "2020-02-01", med),
        ("1007", "Youssef Naguib", "يوسف نجيب", "male", "Technical", "G3", 1, "Senior Engineer", "2019-07-01", med),
        ("1008", "Heba Mostafa", "هبة مصطفى", "female", "Technical", "G2", 3, "Engineer", "2021-11-15", med),
        ("1009", "Omar Sherif", "عمر شريف", "male", "Operations", "G1", 4, "Coordinator", "2022-04-01", med),
        ("1010", "Laila Kamal", "ليلى كمال", "female", "Operations", "G1", 2, "Assistant", "2023-08-01", None),
        ("1011", "Hany Zaki", "هاني زكي", "male", "Sales", "G1", 3, "Sales Rep", "2024-01-15", None),
        ("1012", "Dina Ashraf", "دينا أشرف", "female", "Finance", "G1", 1, "Accounts Clerk", "2025-03-01", med),
    ]
    emps = []
    for code, en, ar, gender, dept, gcode, sp, title, hire, benefit in people:
        g = grades[gcode]
        sal = next((p.monthly_salary for p in g.points if p.point_no == sp),
                   g.points[0].monthly_salary)
        e = Employee(code=code, name=en, name_ar=ar, gender=gender,
                     department_id=depts[dept].id, grade_id=g.id, spine_point=sp,
                     job_title=title, hire_date=date.fromisoformat(hire),
                     basic_salary=round(sal * 0.8), allowances=round(sal * 0.2),
                     national_id="2" + code + "0" * 6,
                     status="active", contract_type="indefinite",
                     benefit_id=benefit.id if benefit else None,
                     bank_name="CIB", bank_account="EG" + code + "00")
        db.session.add(e)
        emps.append(e)

    # a leaver
    leaver = Employee(code="1000", name="Ahmed Sami", name_ar="أحمد سامي",
                      gender="male", department_id=depts["Operations"].id,
                      grade_id=grades["G2"].id, spine_point=2, job_title="Coordinator",
                      hire_date=date(2019, 2, 1), end_date=date(date.today().year, 3, 20),
                      basic_salary=7600, allowances=1900, status="left",
                      contract_type="indefinite")
    db.session.add(leaver)
    db.session.flush()

    # loans
    db.session.add(Loan(employee_id=emps[2].id, principal=12000, monthly_deduction=1000,
                        outstanding=8000, reason="Personal advance"))
    db.session.add(Loan(employee_id=emps[5].id, principal=6000, monthly_deduction=500,
                        outstanding=2500, reason="Emergency"))

    # attendance for the current month (working days SU-TH)
    today = date.today()
    first = today.replace(day=1)
    for e in emps:
        d = first
        while d <= today:
            if d.weekday() not in (4, 5):  # skip Fri, Sat
                worked = 8.0
                if random.random() < 0.06:
                    worked = round(random.choice([0, 4, 6, 7]), 1)
                elif random.random() < 0.10:
                    worked = round(random.choice([9, 9.5, 10]), 1)
                db.session.add(Attendance(
                    employee_id=e.id, work_date=d, hours_worked=worked,
                    expected_hours=8, ot_day_hours=max(0, worked - 8),
                    status="present" if worked else "absent"))
            d += timedelta(days=1)

    # some leave
    db.session.add(Leave(employee_id=emps[3].id, leave_type="sick",
                         start_date=first, end_date=first + timedelta(days=2),
                         days=3, paid_pct=75, note="Flu"))
    db.session.add(Leave(employee_id=emps[7].id, leave_type="annual",
                         start_date=first + timedelta(days=10),
                         end_date=first + timedelta(days=14), days=5))
    db.session.commit()
    print("Demo data seeded.")
