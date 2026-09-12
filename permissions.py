"""Scheme of delegation — roles, capabilities and the editable matrix.

Every editable table carries five capabilities: view, enter, edit,
delete and approve.  The matrix is seeded with a sensible default on
first run and is then editable in the app, so the client's own scheme of
delegation can be set without touching code.

Separation of duties is enforced in the routes: nobody approves a row
they created, whatever the matrix says.
"""
from models import db, RolePermission, get_setting, set_setting
from streams import STREAM_ORDER, STREAMS

ROLES = [
    ("admin", "System Administrator", "مدير النظام"),
    ("md", "Managing Director", "العضو المنتدب"),
    ("cfo", "Chief Financial Officer", "المدير المالي"),
    ("fm", "Finance Manager", "مدير الحسابات"),
    ("accountant", "Accountant", "محاسب"),
    ("treasury", "Treasury / Cashier", "الخزينة"),
    ("data_entry", "Data Entry", "إدخال بيانات"),
    ("viewer", "Viewer", "مشاهدة فقط"),
]
ROLE_KEYS = [r[0] for r in ROLES]
ROLE_LABELS = {r[0]: r[1] for r in ROLES}
ROLE_LABELS_AR = {r[0]: r[2] for r in ROLES}

ACTIONS = [
    ("view", "View", "عرض"),
    ("enter", "Enter", "إدخال"),
    ("edit", "Edit", "تعديل"),
    ("delete", "Delete", "حذف"),
    ("approve", "Review & approve", "مراجعة واعتماد"),
]
ACTION_KEYS = [a[0] for a in ACTIONS]

# --- Core (non-stream) capabilities -------------------------------------
CORE_CAPS = [
    ("dashboard", "Dashboard", "لوحة المتابعة"),
    ("forecast", "Weekly forecast", "التدفق الأسبوعي"),
    ("analysis", "Analysis & statistics", "التحليلات والإحصاءات"),
    ("trend", "Rolling trend forecast", "التوقعات حسب الاتجاه"),
    ("banks_view", "View bank balances", "عرض أرصدة البنوك"),
    ("banks_edit", "Maintain bank balances", "تعديل أرصدة البنوك"),
    ("opening_edit", "Edit opening balances", "تعديل الرصيد الافتتاحي"),
    ("reference_data", "Maintain revenue types & cost categories", "بنود الإيرادات والتكاليف"),
    ("exports", "Export reports", "تصدير التقارير"),
    ("approvals", "Approvals queue", "قائمة الاعتمادات"),
    ("users_admin", "User administration", "إدارة المستخدمين"),
    ("access_control", "Scheme of delegation", "جدول الصلاحيات"),
    ("audit_log", "Audit log", "سجل المراجعة"),
    ("settings", "System settings", "إعدادات النظام"),
]
CORE_CAP_KEYS = [c[0] for c in CORE_CAPS]


def stream_cap(stream_key, action):
    return f"{stream_key}_{action}"


STREAM_CAP_KEYS = [stream_cap(s, a) for s in STREAM_ORDER for a in ACTION_KEYS]
CAP_KEYS = CORE_CAP_KEYS + STREAM_CAP_KEYS

CAP_LABELS = {c[0]: c[1] for c in CORE_CAPS}
CAP_LABELS_AR = {c[0]: c[2] for c in CORE_CAPS}
for _s in STREAM_ORDER:
    for _a, _en, _ar in ACTIONS:
        CAP_LABELS[stream_cap(_s, _a)] = f"{STREAMS[_s]['en']} — {_en}"
        CAP_LABELS_AR[stream_cap(_s, _a)] = f"{STREAMS[_s]['ar']} — {_ar}"


# --- Default scheme of delegation ---------------------------------------
# Per role: the stream actions granted, plus the core capabilities.
DEFAULT_STREAM_ACTIONS = {
    "admin":      ["view", "enter", "edit", "delete", "approve"],
    "md":         ["view", "approve"],
    "cfo":        ["view", "enter", "edit", "approve"],
    "fm":         ["view", "enter", "edit", "delete", "approve"],
    "accountant": ["view", "enter", "edit"],
    "treasury":   ["view", "enter"],
    "data_entry": ["view", "enter"],
    "viewer":     ["view"],
}

DEFAULT_CORE = {
    "admin": CORE_CAP_KEYS,
    "md": ["dashboard", "forecast", "analysis", "trend", "banks_view", "exports", "approvals", "audit_log"],
    "cfo": ["dashboard", "forecast", "analysis", "trend", "banks_view", "banks_edit", "opening_edit",
            "reference_data", "exports", "approvals", "audit_log", "settings"],
    "fm": ["dashboard", "forecast", "analysis", "trend", "banks_view", "banks_edit", "opening_edit",
           "reference_data", "exports", "approvals"],
    "accountant": ["dashboard", "forecast", "analysis", "trend", "banks_view", "exports"],
    "treasury": ["dashboard", "forecast", "banks_view", "exports"],
    "data_entry": ["dashboard", "forecast"],
    "viewer": ["dashboard", "forecast", "analysis", "trend", "banks_view"],
}

#: Roles that may decide items in the approvals queue (editable in settings).
DEFAULT_APPROVERS = ["admin", "cfo", "md", "fm"]

OPEN_ENDPOINTS = {"login", "logout", "setup", "static", "set_lang", "healthz", "brand_org_logo"}


# ============================================================
# Matrix storage
# ============================================================

def seed_matrix(force=False):
    """Write the default matrix on first run. Never overwrites unless forced."""
    if not force and RolePermission.query.first() is not None:
        return
    for role in ROLE_KEYS:
        allowed = set()
        if role == "admin":
            allowed = set(CAP_KEYS)
        else:
            allowed |= set(DEFAULT_CORE.get(role, []))
            for s in STREAM_ORDER:
                for a in DEFAULT_STREAM_ACTIONS.get(role, []):
                    allowed.add(stream_cap(s, a))
        for cap in CAP_KEYS:
            row = db.session.get(RolePermission, (role, cap))
            if row is None:
                row = RolePermission(role=role, cap=cap)
                db.session.add(row)
            row.allowed = cap in allowed
    db.session.commit()


def get_matrix():
    m = {r: {c: False for c in CAP_KEYS} for r in ROLE_KEYS}
    for rp in RolePermission.query.all():
        if rp.role in m and rp.cap in m[rp.role]:
            m[rp.role][rp.cap] = bool(rp.allowed)
    for c in CAP_KEYS:
        m["admin"][c] = True
    return m


def set_permission(role, cap, allowed):
    if role == "admin":
        return
    row = db.session.get(RolePermission, (role, cap))
    if row is None:
        row = RolePermission(role=role, cap=cap)
        db.session.add(row)
    row.allowed = bool(allowed)
    db.session.commit()


def role_key(user):
    if not user or not getattr(user, "is_authenticated", False):
        return ""
    return (user.role or "").lower()


def has_perm(user, cap):
    if not user or not getattr(user, "is_authenticated", False):
        return False
    role = role_key(user)
    if role == "admin":
        return True
    if not cap:
        return True
    row = db.session.get(RolePermission, (role, cap))
    return bool(row and row.allowed)


def can(user, stream_key, action):
    return has_perm(user, stream_cap(stream_key, action))


def visible_streams(user):
    return [s for s in STREAM_ORDER if can(user, s, "view")]


def get_approver_roles():
    raw = get_setting("approver_roles", ",".join(DEFAULT_APPROVERS))
    return [r for r in (raw or "").split(",") if r in ROLE_KEYS]


def set_approver_roles(roles):
    set_setting("approver_roles", ",".join([r for r in roles if r in ROLE_KEYS]))


def can_approve_any(user):
    if role_key(user) == "admin":
        return True
    if role_key(user) not in get_approver_roles():
        return False
    return any(can(user, s, "approve") for s in STREAM_ORDER)


def dim_reason(user, cap, lang="en"):
    if has_perm(user, cap):
        return ""
    label = (CAP_LABELS_AR if lang == "ar" else CAP_LABELS).get(cap, cap)
    if lang == "ar":
        return f"صلاحية «{label}» غير ممنوحة لدورك"
    return f"Your role is not granted “{label}”"
