"""Demo/test data so a fresh install is explorable. Skip in production: SEED_DEMO=false.

The workforce, salaries and departments below are the August 2026 payroll supplied as
test data, mapped onto the Time grading scale (8 grades, spine points).
"""
from datetime import date, timedelta
import random
from models import (CompanySettings, Department, Grade, SpinePoint, Employee,
                    BenefitPlan, Loan, Attendance, Leave, User)


def run(db):
    for email, name, role in [("hr@time.eg", "Mona Adel (HR)", "hr"),
                              ("finance@time.eg", "Ayat Abd ElWahab (Finance Manager)", "finance_manager"),
                              ("md@time.eg", "Shahenda ElGhaluony (MD)", "md")]:
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
    for en, ar in [("Management", "الإدارة"), ("Administration", "الشؤون الإدارية"),
                   ("Logistics", "اللوجستيات"), ("Marketing", "التسويق"),
                   ("Finance", "المالية"), ("Sales", "المبيعات"),
                   ("Technical Service", "الخدمة الفنية"), ("Legal", "الشؤون القانونية"),
                   ("IT", "تقنية المعلومات"), ("Customer Service", "خدمة العملاء"),
                   ("Other", "أخرى")]:
        d = Department(name=en, name_ar=ar)
        db.session.add(d)
        depts[en] = d
    db.session.flush()

    grade_defs = [
        ("G1", "Support", "الدعم", 1, [5000, 6000, 7000]),
        ("G2", "Junior / Assistant", "مبتدئ / مساعد", 2, [7000, 8000, 9000, 10000]),
        ("G3", "Officer / Coordinator", "أخصائي / منسق", 3, [10000, 11000, 12000, 13000, 14000]),
        ("G4", "Specialist / Engineer", "متخصص / مهندس", 4, [14000, 15000, 16000, 17000, 18000]),
        ("G5", "Senior / Team Leader", "أول / قائد فريق", 5, [18000, 20000, 22000, 24000]),
        ("G6", "Manager", "مدير", 6, [24000, 27000, 30000, 33000]),
        ("G7", "Senior Manager / Head", "مدير أول / رئيس قطاع", 7, [33000, 36000, 40000, 44000]),
        ("G8", "Director / VP", "مدير عام / نائب رئيس", 8, [44000, 50000, 56000, 62000]),
    ]
    grades = {}
    for code, name, name_ar, order, sals in grade_defs:
        g = Grade(code=code, name=name, name_ar=name_ar, order=order)
        db.session.add(g); db.session.flush()
        for i, sal in enumerate(sals, start=1):
            db.session.add(SpinePoint(grade_id=g.id, point_no=i, monthly_salary=sal))
        grades[code] = g

    med = BenefitPlan(name="Standard medical cover", name_ar="تأمين طبي أساسي",
                      provider="MedNet Egypt", employer_cost=450, employee_cost=150,
                      coverage="Outpatient, inpatient, pharmacy — EGP 200k/yr limit")
    med_plus = BenefitPlan(name="Family medical cover", name_ar="تأمين طبي عائلي",
                           provider="MedNet Egypt", employer_cost=900, employee_cost=350,
                           coverage="Employee + dependants, dental & optical")
    db.session.add_all([med, med_plus]); db.session.flush()

    people = [
        ("1", "Shahenda ElGhaluony", "Management", "G6", 3, "Vice President", "2023-01-03", 30000, 0, "indefinite", "Bank"),
        ("2", "Menna Elabd", "Administration", "G3", 3, "Administrative Coordinator", "2025-02-02", 12000, 0, "indefinite", "Bank"),
        ("3", "Lina Mostafa", "Logistics", "G5", 2, "International Supply Chain Manager", "2023-06-18", 20000, 0, "indefinite", "Bank"),
        ("4", "Mariam Ehab", "Marketing", "G6", 2, "Marketing Manager", "2023-06-04", 27000, 0, "indefinite", "Bank"),
        ("5", "Eslam Sayed", "Marketing", "G2", 1, "Content Creator", "2023-06-01", 7000, 0, "part_time", "Bank"),
        ("6", "Seif Aman", "Marketing", "G4", 2, "Graphic Designer", "2025-05-20", 15000, 0, "indefinite", "Bank"),
        ("7", "Yasmin Ali", "Marketing", "G1", 1, "Media Buyer", "2024-01-01", 2500, 0, "part_time", "Bank"),
        ("8", "Zeyad Yasser", "Marketing", "G3", 1, "Reel Creator", "2025-10-12", 10000, 0, "indefinite", "InstaPay"),
        ("9", "Ayat Abd ElWahab", "Finance", "G7", 3, "Accounting Manager", "2026-06-21", 40000, 0, "indefinite", "Bank"),
        ("10", "Ahmed Emad", "Finance", "G5", 2, "Senior Accountant", "2026-07-12", 20000, 0, "indefinite", "Bank"),
        ("11", "Mohamed Rehan", "Finance", "G4", 2, "Logistics Officer", "2023-07-24", 15000, 0, "indefinite", "Bank"),
        ("12", "Ahmed Rabea", "Finance", "G2", 1, "Accountant", "2024-01-01", 7000, 0, "part_time", "InstaPay"),
        ("13", "Ziad Ashraf", "Sales", "G4", 2, "Sales Team Leader", "2024-07-02", 15000, 0, "indefinite", "Bank"),
        ("14", "Noura Farouk", "Sales", "G6", 1, "Lab Sales Manager", "2023-06-11", 25000, 0, "indefinite", "Bank"),
        ("15", "Youssef Saeed", "Sales", "G5", 1, "Materials Sales Manager", "2025-11-15", 18000, 0, "indefinite", "Cash"),
        ("16", "Mohamed Adel", "Sales", "G4", 3, "Product Manager", "2024-05-01", 16000, 0, "indefinite", "Bank"),
        ("17", "Mohamed Bebars", "Technical Service", "G6", 3, "Technical Service Manager", "2023-07-03", 30000, 3000, "indefinite", "Bank"),
        ("18", "Hamza Elsheikh", "Technical Service", "G4", 3, "Technical Service Engineer", "2024-08-01", 16000, 3000, "indefinite", "Bank"),
        ("19", "Mohamed Hamada", "Technical Service", "G3", 3, "Technical Service Engineer", "2024-11-01", 12000, 0, "indefinite", "Bank"),
        ("20", "Tarek Abo Elela", "Technical Service", "G3", 3, "Technical Service Engineer", "2025-11-02", 12000, 0, "indefinite", "Bank"),
        ("21", "Yassin Amr", "Technical Service", "G2", 1, "Technical Service Assistant", "2026-06-29", 7000, 0, "part_time", "InstaPay"),
        ("22", "Ali Hashem", "Legal", "G1", 1, "Lawyer", "2024-01-01", 5000, 0, "part_time", "InstaPay"),
        ("23", "Emad Moussa", "Legal", "G2", 2, "Lawyer", "2026-01-25", 8000, 0, "part_time", "InstaPay"),
        ("24", "Mohamed Nagi", "IT", "G2", 2, "IT Specialist", "2025-10-26", 8000, 0, "indefinite", "InstaPay"),
        ("25", "Khalid Salah", "Customer Service", "G5", 2, "CS Coordinator", "2024-11-24", 20000, 0, "indefinite", "Bank"),
        ("26", "Atef Ahmed", "Other", "G3", 3, "Logistics Officer", "2023-05-14", 12000, 0, "indefinite", "Bank"),
        ("27", "Ayman Elsayd", "Other", "G4", 2, "Driver", "2024-02-13", 15000, 0, "indefinite", "Bank"),
        ("28", "Ahmed Abd Elsalam", "Other", "G2", 1, "Logistics Officer", "2025-04-05", 7500, 2500, "part_time", "InstaPay"),
        ("29", "Kamar Abdo", "Other", "G1", 3, "Cleaning Supervisor", "2024-02-07", 7000, 0, "indefinite", "Bank"),
        ("30", "Mohamed Elbagoury", "Other", "G1", 2, "Admin Assistant", "2026-07-26", 6000, 0, "indefinite", "Bank"),
    ]
    emps = {}
    for code, name, dept, gcode, pt, title, hire, basic, allow, ctype, bank in people:
        e = Employee(code=code, name=name, department_id=depts[dept].id,
                     grade_id=grades[gcode].id, spine_point=pt, job_title=title,
                     hire_date=date.fromisoformat(hire), basic_salary=basic,
                     allowances=allow, status="active", contract_type=ctype,
                     bank_name=bank, bank_account="")
        db.session.add(e); emps[code] = e

    for code in ("1", "4", "9", "17"):
        emps[code].benefit_id = med_plus.id
    for code in ("2", "6", "10", "16", "25"):
        emps[code].benefit_id = med.id

    leaver = Employee(code="900", name="Omar Kamal", department_id=depts["Sales"].id,
                      grade_id=grades["G3"].id, spine_point=2, job_title="Sales Rep",
                      hire_date=date(2022, 3, 1),
                      end_date=date(date.today().year, max(1, date.today().month - 1), 15),
                      basic_salary=11000, allowances=0, status="left",
                      contract_type="indefinite", bank_name="Bank")
    db.session.add(leaver); db.session.flush()

    db.session.add(Loan(employee_id=emps["11"].id, principal=12000, monthly_deduction=1000,
                        outstanding=8000, reason="Personal advance"))
    db.session.add(Loan(employee_id=emps["6"].id, principal=6000, monthly_deduction=500,
                        outstanding=2500, reason="Emergency"))

    today = date.today(); first = today.replace(day=1)
    for e in emps.values():
        d = first
        while d <= today:
            if d.weekday() not in (4, 5):
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

    db.session.add(Leave(employee_id=emps["2"].id, leave_type="sick",
                         start_date=first, end_date=first + timedelta(days=2),
                         days=3, paid_pct=75, note="Flu"))
    db.session.add(Leave(employee_id=emps["8"].id, leave_type="annual",
                         start_date=first + timedelta(days=10),
                         end_date=first + timedelta(days=14), days=5))
    db.session.commit()
    print("Demo data seeded.")
