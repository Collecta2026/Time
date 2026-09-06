# Bilingual strings for Time. Key -> {"en": ..., "ar": ...}
# t(key) resolves against the current language held in the Flask session.

STRINGS = {
    # Brand / chrome
    "app_name": {"en": "Time", "ar": "تايم"},
    "app_tagline": {"en": "Scientific Gate HR", "ar": "الموارد البشرية — بوابة العلوم"},
    "language": {"en": "العربية", "ar": "English"},   # label shows the *other* language
    "logout": {"en": "Sign out", "ar": "تسجيل الخروج"},
    "signin": {"en": "Sign in", "ar": "تسجيل الدخول"},
    "email": {"en": "Email", "ar": "البريد الإلكتروني"},
    "password": {"en": "Password", "ar": "كلمة المرور"},
    "search": {"en": "Search", "ar": "بحث"},
    "save": {"en": "Save", "ar": "حفظ"},
    "cancel": {"en": "Cancel", "ar": "إلغاء"},
    "add": {"en": "Add", "ar": "إضافة"},
    "edit": {"en": "Edit", "ar": "تعديل"},
    "delete": {"en": "Delete", "ar": "حذف"},
    "actions": {"en": "Actions", "ar": "إجراءات"},
    "back": {"en": "Back", "ar": "رجوع"},
    "print": {"en": "Print", "ar": "طباعة"},
    "export": {"en": "Export", "ar": "تصدير"},
    "all": {"en": "All", "ar": "الكل"},
    "none": {"en": "None", "ar": "لا يوجد"},
    "total": {"en": "Total", "ar": "الإجمالي"},

    # Navigation
    "nav_dashboard": {"en": "Dashboard", "ar": "لوحة التحكم"},
    "nav_employees": {"en": "Employees", "ar": "الموظفون"},
    "nav_grades": {"en": "Grades & Spine", "ar": "الدرجات والنقاط"},
    "nav_departments": {"en": "Departments", "ar": "الأقسام"},
    "nav_attendance": {"en": "Attendance", "ar": "الحضور"},
    "nav_leave": {"en": "Leave", "ar": "الإجازات"},
    "nav_loans": {"en": "Loans", "ar": "السلف"},
    "nav_benefits": {"en": "Medical benefits", "ar": "المزايا الطبية"},
    "nav_payroll": {"en": "Payroll", "ar": "الرواتب"},
    "nav_reports": {"en": "Reports", "ar": "التقارير"},
    "nav_settings": {"en": "Settings", "ar": "الإعدادات"},

    # Dashboard
    "headcount": {"en": "Headcount", "ar": "عدد الموظفين"},
    "active_employees": {"en": "Active employees", "ar": "الموظفون النشطون"},
    "monthly_payroll": {"en": "Monthly gross payroll", "ar": "إجمالي الرواتب الشهرية"},
    "employer_cost": {"en": "Employer cost", "ar": "تكلفة صاحب العمل"},
    "outstanding_loans": {"en": "Outstanding loans", "ar": "السلف المستحقة"},
    "starters_ytd": {"en": "Starters (YTD)", "ar": "المعينون (السنة)"},
    "leavers_ytd": {"en": "Leavers (YTD)", "ar": "المغادرون (السنة)"},
    "by_department": {"en": "Headcount by department", "ar": "الموظفون حسب القسم"},
    "recent_hires": {"en": "Recent hires", "ar": "أحدث التعيينات"},

    # Employee fields
    "code": {"en": "Employee code", "ar": "كود الموظف"},
    "name": {"en": "Name", "ar": "الاسم"},
    "name_ar": {"en": "Name (Arabic)", "ar": "الاسم بالعربية"},
    "national_id": {"en": "National ID", "ar": "الرقم القومي"},
    "gender": {"en": "Gender", "ar": "النوع"},
    "male": {"en": "Male", "ar": "ذكر"},
    "female": {"en": "Female", "ar": "أنثى"},
    "dob": {"en": "Date of birth", "ar": "تاريخ الميلاد"},
    "phone": {"en": "Phone", "ar": "الهاتف"},
    "address": {"en": "Address", "ar": "العنوان"},
    "department": {"en": "Department", "ar": "القسم"},
    "job_title": {"en": "Job title", "ar": "المسمى الوظيفي"},
    "grade": {"en": "Grade", "ar": "الدرجة"},
    "spine_point": {"en": "Spine point", "ar": "نقطة الدرجة"},
    "hire_date": {"en": "Start date", "ar": "تاريخ التعيين"},
    "end_date": {"en": "End date", "ar": "تاريخ الانتهاء"},
    "status": {"en": "Status", "ar": "الحالة"},
    "active": {"en": "Active", "ar": "نشط"},
    "left": {"en": "Left", "ar": "مغادر"},
    "contract_type": {"en": "Contract type", "ar": "نوع العقد"},
    "indefinite": {"en": "Indefinite", "ar": "غير محدد المدة"},
    "fixed": {"en": "Fixed term", "ar": "محدد المدة"},
    "probation": {"en": "Probation", "ar": "تحت الاختبار"},
    "basic_salary": {"en": "Basic salary", "ar": "الراتب الأساسي"},
    "allowances": {"en": "Allowances", "ar": "البدلات"},
    "insurable_wage": {"en": "Insurable wage", "ar": "أجر التأمين"},
    "bank_name": {"en": "Bank", "ar": "البنك"},
    "bank_account": {"en": "Account / IBAN", "ar": "الحساب / الآيبان"},
    "years_service": {"en": "Years of service", "ar": "سنوات الخدمة"},
    "contract": {"en": "Contract", "ar": "العقد"},
    "payslips": {"en": "Payslips", "ar": "قسائم الراتب"},
    "new_employee": {"en": "New employee", "ar": "موظف جديد"},

    # Grades
    "grade_code": {"en": "Code", "ar": "الكود"},
    "grade_name": {"en": "Grade name", "ar": "اسم الدرجة"},
    "points": {"en": "Spine points", "ar": "نقاط الدرجة"},
    "monthly_salary": {"en": "Monthly salary", "ar": "الراتب الشهري"},
    "add_point": {"en": "Add point", "ar": "إضافة نقطة"},
    "new_grade": {"en": "New grade", "ar": "درجة جديدة"},
    "headroom": {"en": "Room to grow", "ar": "مجال للترقي"},

    # Attendance
    "import_attendance": {"en": "Import from fingerprint", "ar": "استيراد من البصمة"},
    "work_date": {"en": "Date", "ar": "التاريخ"},
    "hours_worked": {"en": "Hours worked", "ar": "ساعات العمل"},
    "expected_hours": {"en": "Expected", "ar": "المتوقع"},
    "overtime": {"en": "Overtime", "ar": "عمل إضافي"},
    "shortfall": {"en": "Shortfall", "ar": "عجز الساعات"},
    "download_template": {"en": "Download CSV template", "ar": "تحميل قالب CSV"},
    "upload_csv": {"en": "Upload CSV", "ar": "رفع ملف CSV"},
    "import_help": {"en": "Columns: employee_code, date (YYYY-MM-DD), hours_worked — or time_in/time_out.",
                    "ar": "الأعمدة: كود الموظف، التاريخ (سنة-شهر-يوم)، ساعات العمل — أو وقت الدخول/الخروج."},

    # Leave
    "leave_type": {"en": "Leave type", "ar": "نوع الإجازة"},
    "annual": {"en": "Annual", "ar": "سنوية"},
    "sick": {"en": "Sick", "ar": "مرضية"},
    "casual": {"en": "Casual", "ar": "عارضة"},
    "maternity": {"en": "Maternity", "ar": "وضع"},
    "unpaid": {"en": "Unpaid", "ar": "بدون أجر"},
    "days": {"en": "Days", "ar": "أيام"},
    "paid_pct": {"en": "Paid %", "ar": "نسبة الأجر %"},
    "record_leave": {"en": "Record leave", "ar": "تسجيل إجازة"},

    # Loans
    "principal": {"en": "Principal", "ar": "أصل السلفة"},
    "monthly_deduction": {"en": "Monthly deduction", "ar": "الاستقطاع الشهري"},
    "outstanding": {"en": "Outstanding", "ar": "المتبقي"},
    "issue_date": {"en": "Issue date", "ar": "تاريخ الصرف"},
    "reason": {"en": "Reason", "ar": "السبب"},
    "new_loan": {"en": "New loan", "ar": "سلفة جديدة"},
    "settled": {"en": "Settled", "ar": "مسددة"},

    # Benefits
    "provider": {"en": "Provider", "ar": "مقدم الخدمة"},
    "employer_share": {"en": "Employer / month", "ar": "حصة صاحب العمل شهرياً"},
    "employee_share": {"en": "Employee / month", "ar": "حصة الموظف شهرياً"},
    "coverage": {"en": "Coverage", "ar": "التغطية"},
    "members": {"en": "Members", "ar": "المشتركون"},
    "new_plan": {"en": "New plan", "ar": "خطة جديدة"},

    # Payroll
    "new_run": {"en": "New payroll run", "ar": "تشغيل رواتب جديد"},
    "period": {"en": "Period", "ar": "الفترة"},
    "run": {"en": "Run payroll", "ar": "تشغيل الرواتب"},
    "finalise": {"en": "Finalise", "ar": "اعتماد"},
    "draft": {"en": "Draft", "ar": "مسودة"},
    "finalised": {"en": "Finalised", "ar": "معتمد"},
    "gross": {"en": "Gross", "ar": "الإجمالي"},
    "si_employee": {"en": "Social insurance (11%)", "ar": "تأمينات الموظف (11%)"},
    "si_employer": {"en": "Employer insurance (18.75%)", "ar": "تأمينات صاحب العمل (18.75%)"},
    "income_tax": {"en": "Income tax", "ar": "ضريبة الدخل"},
    "deductions": {"en": "Deductions", "ar": "الاستقطاعات"},
    "net_pay": {"en": "Net pay", "ar": "صافي الراتب"},
    "payslip": {"en": "Payslip", "ar": "قسيمة الراتب"},
    "earnings": {"en": "Earnings", "ar": "المستحقات"},
    "employer_contributions": {"en": "Employer contributions (not deducted)",
                               "ar": "مساهمات صاحب العمل (غير مستقطعة)"},
    "emergency_fund": {"en": "Emergency fund (1%)", "ar": "صندوق الطوارئ (1%)"},

    # Reports
    "rep_attendance": {"en": "Attendance report", "ar": "تقرير الحضور"},
    "rep_sick": {"en": "Sick days report", "ar": "تقرير الإجازات المرضية"},
    "rep_starters_leavers": {"en": "Starters & leavers", "ar": "المعينون والمغادرون"},
    "rep_stats": {"en": "Management statistics", "ar": "إحصاءات الإدارة"},
    "rep_payroll_summary": {"en": "Payroll summary", "ar": "ملخص الرواتب"},
    "rep_si": {"en": "Social insurance schedule", "ar": "جدول التأمينات"},
    "rep_loans": {"en": "Loan register", "ar": "سجل السلف"},
    "from_date": {"en": "From", "ar": "من"},
    "to_date": {"en": "To", "ar": "إلى"},
    "avg_salary": {"en": "Average salary", "ar": "متوسط الراتب"},
    "turnover": {"en": "Turnover rate", "ar": "معدل الدوران"},

    # Contract
    "employment_contract": {"en": "Employment contract", "ar": "عقد عمل"},

    # Misc
    "confirm_delete": {"en": "Delete this record?", "ar": "حذف هذا السجل؟"},
    "saved": {"en": "Saved.", "ar": "تم الحفظ."},
    "no_records": {"en": "Nothing here yet.", "ar": "لا توجد سجلات بعد."},

    # Workflow states
    "prepared": {"en": "Prepared", "ar": "تم الإعداد"},
    "approved": {"en": "Approved", "ar": "معتمد"},
    "authorised": {"en": "Authorised", "ar": "مُصرّح بالدفع"},
    "paid": {"en": "Paid", "ar": "مدفوع"},
    # Workflow actions
    "submit_approval": {"en": "Submit for approval", "ar": "إرسال للاعتماد"},
    "approve": {"en": "Approve (Finance Manager)", "ar": "اعتماد (مدير مالي)"},
    "authorise": {"en": "Authorise for payment (MD)", "ar": "تصريح بالدفع (العضو المنتدب)"},
    "reject": {"en": "Return to HR", "ar": "إعادة للموارد البشرية"},
    "mark_paid": {"en": "Mark as paid", "ar": "تحديد كمدفوع"},
    "payment_schedule": {"en": "Payment schedule", "ar": "جدول الدفع"},
    "delegation_trail": {"en": "Approval trail", "ar": "مسار الاعتماد"},
    "prepared_by": {"en": "Prepared by", "ar": "أعدّه"},
    "approved_by": {"en": "Approved by", "ar": "اعتمده"},
    "authorised_by": {"en": "Authorised by", "ar": "صرّح به"},
    "paid_by": {"en": "Paid by", "ar": "سدّده"},
    "awaiting": {"en": "Awaiting", "ar": "في انتظار"},
    "returned_reason": {"en": "Returned", "ar": "أُعيد"},

    # Roles
    "role": {"en": "Role", "ar": "الدور"},
    "role_admin": {"en": "Administrator", "ar": "مدير النظام"},
    "role_hr": {"en": "HR (preparer)", "ar": "موارد بشرية (معد)"},
    "role_finance_manager": {"en": "Finance Manager", "ar": "المدير المالي"},
    "role_md": {"en": "Managing Director", "ar": "العضو المنتدب"},
    "role_viewer": {"en": "Viewer", "ar": "مُطّلع"},

    # Admin / audit / delegation
    "nav_users": {"en": "Users", "ar": "المستخدمون"},
    "nav_audit": {"en": "Audit log", "ar": "سجل التدقيق"},
    "new_user": {"en": "New user", "ar": "مستخدم جديد"},
    "scheme_delegation": {"en": "Scheme of delegation", "ar": "لائحة تفويض الصلاحيات"},
    "band": {"en": "Band", "ar": "الشريحة"},
    "min_amount": {"en": "From (net)", "ar": "من (الصافي)"},
    "max_amount": {"en": "To (net)", "ar": "إلى (الصافي)"},
    "requires_fm": {"en": "Finance Manager", "ar": "المدير المالي"},
    "requires_md": {"en": "MD joint release", "ar": "تصريح مشترك للعضو المنتدب"},
    "paying_bank": {"en": "Paying bank", "ar": "بنك الصرف"},
    "remittances": {"en": "Statutory remittances", "ar": "التوريدات القانونية"},
    "to_tax_authority": {"en": "Income tax — to Tax Authority", "ar": "ضريبة الدخل — لمصلحة الضرائب"},
    "to_nosi": {"en": "Social insurance — to NOSI", "ar": "التأمينات — للهيئة القومية للتأمين"},
    "total_net_pay": {"en": "Total net pay to disburse", "ar": "إجمالي صافي الأجور للصرف"},
    "when": {"en": "When", "ar": "التوقيت"},
    "actor": {"en": "User", "ar": "المستخدم"},
    "action": {"en": "Action", "ar": "الإجراء"},

    # SI remittance
    "insurance_schedule": {"en": "Insurance remittance schedule", "ar": "كشف توريد التأمينات"},
    "rep_si_register": {"en": "Insurance remittance register", "ar": "سجل توريد التأمينات"},
    "remittance_total": {"en": "Total remittance", "ar": "إجمالي التوريد"},
    "insurance_no": {"en": "Insurance registration no.", "ar": "رقم الاشتراك التأميني"},

    # Leave provision
    "rep_leave_provision": {"en": "Leave pay provision", "ar": "مخصص أجر الإجازات"},
    "entitlement_days": {"en": "Entitlement (days)", "ar": "الاستحقاق (أيام)"},
    "accrued_days": {"en": "Accrued (days)", "ar": "المستحق (أيام)"},
    "taken_days": {"en": "Taken (days)", "ar": "المستخدم (أيام)"},
    "balance_days": {"en": "Balance (days)", "ar": "الرصيد (أيام)"},
    "daily_rate": {"en": "Daily rate", "ar": "أجر اليوم"},
    "provision_value": {"en": "Provision value", "ar": "قيمة المخصص"},
    "monthly_accrual": {"en": "Month accrual", "ar": "مخصص الشهر"},
    "total_liability": {"en": "Total leave liability", "ar": "إجمالي التزام الإجازات"},
    "post_provision": {"en": "Post provision for this month", "ar": "ترحيل مخصص الشهر"},
    "posted": {"en": "Posted", "ar": "مُرحّل"},
    "movement": {"en": "Monthly movement", "ar": "الحركة الشهرية"},

    # Help
    "nav_help": {"en": "Help", "ar": "المساعدة"},
}


def translate(key, lang):
    entry = STRINGS.get(key)
    if not entry:
        return key
    return entry.get(lang) or entry.get("en") or key
