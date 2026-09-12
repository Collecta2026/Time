"""Bilingual user interface — English and Arabic.

`t(key)` returns the string for the active language, falling back to
English and then to the key itself, so a missing translation degrades
visibly but never breaks a page.  Arabic renders right-to-left; the
layout direction comes from `direction()`.
"""
from flask import session

LANGS = [("en", "English", "English"), ("ar", "العربية", "Arabic")]
LANG_KEYS = [l[0] for l in LANGS]

T = {
    # --- chrome -----------------------------------------------------
    "app_name": ("Cash Flow Budgeting System", "نظام موازنة التدفقات النقدية"),
    "dashboard": ("Dashboard", "لوحة المتابعة"),
    "forecast": ("Weekly Forecast", "التدفق النقدي الأسبوعي"),
    "analysis": ("Analysis", "التحليلات"),
    "tables": ("Data Tables", "جداول البيانات"),
    "inflows": ("Cash In", "المتحصلات"),
    "outflows": ("Cash Out", "المدفوعات"),
    "banks": ("Bank & Cash Accounts", "الحسابات البنكية والنقدية"),
    "opening_balances": ("Opening Balances", "الأرصدة الافتتاحية"),
    "approvals": ("Approvals", "الاعتمادات"),
    "delegation": ("Scheme of Delegation", "جدول الصلاحيات"),
    "users": ("Users", "المستخدمون"),
    "audit": ("Audit Log", "سجل المراجعة"),
    "settings": ("Settings", "الإعدادات"),
    "reference": ("Revenue & Cost Categories", "بنود الإيرادات والتكاليف"),
    "logout": ("Sign out", "تسجيل الخروج"),
    "login": ("Sign in", "تسجيل الدخول"),
    "username": ("Username", "اسم المستخدم"),
    "password": ("Password", "كلمة المرور"),
    "language": ("Language", "اللغة"),
    "help": ("Help", "المساعدة"),

    # --- generic actions --------------------------------------------
    "add": ("Add", "إضافة"),
    "edit": ("Edit", "تعديل"),
    "save": ("Save", "حفظ"),
    "cancel": ("Cancel", "إلغاء"),
    "delete": ("Delete", "حذف"),
    "submit_for_approval": ("Submit for approval", "إرسال للاعتماد"),
    "approve": ("Approve", "اعتماد"),
    "reject": ("Reject", "رفض"),
    "search": ("Search", "بحث"),
    "filter": ("Filter", "تصفية"),
    "export": ("Export", "تصدير"),
    "back": ("Back", "رجوع"),
    "confirm_delete": ("Delete this entry? This cannot be undone.",
                       "هل تريد حذف هذا السجل؟ لا يمكن التراجع."),
    "no_rows": ("No entries yet.", "لا توجد سجلات بعد."),
    "actions": ("Actions", "إجراءات"),
    "total": ("Total", "الإجمالي"),
    "all": ("All", "الكل"),
    "none": ("None", "لا شيء"),
    "yes": ("Yes", "نعم"),
    "no": ("No", "لا"),
    "required_field": ("This field is required", "هذا الحقل مطلوب"),

    # --- money & time ------------------------------------------------
    "currency": ("Currency", "العملة"),
    "amount": ("Amount", "المبلغ"),
    "egp": ("EGP", "جنيه"),
    "usd": ("USD", "دولار"),
    "egp_equivalent": ("EGP equivalent", "ما يعادله بالجنيه"),
    "fx_rate": ("USD → EGP rate", "سعر صرف الدولار"),
    "week": ("Week", "الأسبوع"),
    "week_commencing": ("Week commencing", "أسبوع يبدأ"),
    "date": ("Date", "التاريخ"),
    "from": ("From", "من"),
    "to": ("To", "إلى"),

    # --- forecast ----------------------------------------------------
    "opening": ("Opening", "رصيد أول المدة"),
    "closing": ("Closing", "رصيد آخر المدة"),
    "cash_in": ("Cash in", "متحصلات"),
    "cash_out": ("Cash out", "مدفوعات"),
    "net_movement": ("Net movement", "صافي الحركة"),
    "pending": ("Pending approval", "بانتظار الاعتماد"),
    "committed": ("Approved", "معتمد"),
    "overridden": ("Overridden", "معدّل يدوياً"),
    "rolled_over": ("Rolled over", "مرحّل"),
    "next_6_weeks": ("Next {n} weeks", "الأسابيع الـ {n} القادمة"),
    "lowest_balance": ("Lowest balance", "أدنى رصيد"),
    "detail": ("Detail", "التفاصيل"),
    "week_detail": ("Movements in this week", "حركات هذا الأسبوع"),

    # --- alerts ------------------------------------------------------
    "alerts": ("Alerts", "التنبيهات"),
    "no_alerts": ("No shortages forecast in this period.",
                  "لا يوجد عجز متوقع خلال هذه الفترة."),
    "alert_overdrawn": ("Forecast shortage — balance goes negative",
                        "عجز متوقع — الرصيد يصبح سالباً"),
    "alert_below_buffer": ("Balance falls below the minimum buffer",
                           "الرصيد يقل عن الحد الأدنى المطلوب"),
    "first_shortage": ("First shortage", "أول عجز متوقع"),
    "no_shortage_horizon": ("No shortage across the full horizon",
                            "لا يوجد عجز خلال كامل الفترة"),

    # --- workflow ----------------------------------------------------
    "status": ("Status", "الحالة"),
    "status_draft": ("Draft", "مسودة"),
    "status_submitted": ("Submitted", "مُرسل"),
    "status_approved": ("Approved", "معتمد"),
    "status_rejected": ("Rejected", "مرفوض"),
    "status_cancelled": ("Cancelled", "ملغي"),
    "status_settled": ("Settled", "تم السداد"),
    "entered_by": ("Entered by", "أدخله"),
    "approved_by": ("Approved by", "اعتمده"),
    "reviewed_by": ("Reviewed by", "راجعه"),
    "no_self_approve": ("Separation of duties: you cannot approve your own entry.",
                        "الفصل بين المهام: لا يمكنك اعتماد ما أدخلته بنفسك."),
    "pending_count": ("{n} awaiting approval", "{n} بانتظار الاعتماد"),

    # --- banks / opening ---------------------------------------------
    "account_name": ("Account", "الحساب"),
    "bank_name": ("Bank", "البنك"),
    "account_no": ("Account no.", "رقم الحساب"),
    "balance": ("Balance", "الرصيد"),
    "as_at": ("As at", "كما في"),
    "include_in_forecast": ("In forecast", "ضمن التوقعات"),
    "overdraft_limit": ("Overdraft limit", "حد السحب على المكشوف"),
    "opening_help": ("The opening balance rolls forward from the previous week's closing "
                     "balance. Enter a figure here to pin a week to an actual bank balance.",
                     "يُرحَّل الرصيد الافتتاحي من رصيد نهاية الأسبوع السابق. أدخل رقماً هنا "
                     "لتثبيت رصيد الأسبوع على الرصيد البنكي الفعلي."),
    "reset_to_rollover": ("Reset to rolled-over figure", "العودة للرصيد المرحّل"),

    # --- analysis ----------------------------------------------------
    "revenue_by_type": ("Revenue by type", "الإيرادات حسب النوع"),
    "cost_by_category": ("Cost elements", "عناصر التكلفة"),
    "pct_of_revenue": ("% of revenue", "% من الإيرادات"),
    "pct_of_cost": ("% of cost", "% من التكاليف"),
    "cost_ratio": ("Total cost as % of revenue", "إجمالي التكاليف كنسبة من الإيرادات"),

    # --- trend forecast ----------------------------------------------
    "trend": ("Trend Forecast", "التوقعات حسب الاتجاه"),
    "trend_intro": ("Rolled forward from the trend of the previous {n} weeks, element by element.",
                    "مُرحَّلة وفقاً لاتجاه الأسابيع الـ {n} السابقة، لكل بند على حدة."),
    "lookback": ("Weeks of history", "أسابيع الاتجاه"),
    "project_ahead": ("Weeks projected", "أسابيع التوقع"),
    "method": ("Method", "الأسلوب"),
    "method_linear": ("Linear trend", "اتجاه خطي"),
    "method_average": ("Flat average", "المتوسط"),
    "history_total": ("Last {n} weeks", "آخر {n} أسابيع"),
    "weekly_average": ("Weekly average", "المتوسط الأسبوعي"),
    "trend_per_week": ("Trend / week", "الاتجاه أسبوعياً"),
    "projected": ("Projected", "متوقع"),
    "booked": ("Booked", "مسجل"),
    "variance": ("Variance", "الفرق"),
    "variance_help": ("Booked less projected. A negative figure means less is booked than the trend suggests.",
                      "المسجل ناقص المتوقع. الرقم السالب يعني أن المسجل أقل مما يشير إليه الاتجاه."),
    "projected_position": ("Projected cash position", "الوضع النقدي المتوقع"),
    "booked_position": ("Booked position", "الوضع المسجل"),
    "no_history": ("No history in the trend window — the projection needs past entries to measure.",
                   "لا توجد بيانات سابقة في فترة الاتجاه — يحتاج التوقع إلى سجلات سابقة."),

    # --- weekly planner ----------------------------------------------
    "weekly_planner": ("Weekly Planner", "الخطة الأسبوعية"),
    "weekly_view": ("Weekly view", "عرض أسبوعي"),
    "list_view": ("List view", "عرض القائمة"),
    "collection_type": ("Collection type", "نوع التحصيل"),
    "customer_no": ("Customer no.", "رقم العميل"),
    "planner_intro": ("Every entry placed in the week its cash is expected, grouped by type.",
                      "كل سجل في الأسبوع المتوقع تحصيله، مجمّعاً حسب النوع."),

    # --- settings ----------------------------------------------------
    "work_week": ("Working week", "أيام العمل"),
    "weekend_rule": ("Non-working day rule", "معالجة أيام العطلات"),
    "horizon_weeks": ("Forecast horizon (weeks)", "مدى التوقعات (أسابيع)"),
    "dashboard_weeks": ("Dashboard weeks", "أسابيع لوحة المتابعة"),
    "min_buffer": ("Minimum cash buffer", "الحد الأدنى للرصيد"),
    "include_pending": ("Include unapproved entries in the forecast",
                        "إدراج البنود غير المعتمدة في التوقعات"),
    "apply_certainty": ("Weight expected receipts by certainty %",
                        "ترجيح المتحصلات بنسبة التأكد"),
    "org_name": ("Organisation name", "اسم المنشأة"),
    "product_name": ("System name", "اسم النظام"),
    "saved": ("Saved.", "تم الحفظ."),
}


def lang():
    from models import get_setting
    v = session.get("lang")
    if v in LANG_KEYS:
        return v
    try:
        d = get_setting("default_lang", "en")
    except Exception:
        d = "en"
    return d if d in LANG_KEYS else "en"


def set_lang(v):
    if v in LANG_KEYS:
        session["lang"] = v


def direction(l=None):
    return "rtl" if (l or lang()) == "ar" else "ltr"


def t(key, **kw):
    pair = T.get(key)
    if not pair:
        return key
    s = pair[1] if lang() == "ar" and pair[1] else pair[0]
    if kw:
        try:
            s = s.format(**kw)
        except (KeyError, IndexError):
            pass
    return s


def pick(en, ar):
    """Choose between two ready-made strings (used for model-held labels)."""
    return ar if (lang() == "ar" and ar) else en
