"""Scientific Gate — Cash Flow Budgeting System (Flask / Postgres).

Release 1: data model, the ten editable forecast tables, bank and
opening-balance maintenance, the scheme of delegation with an approvals
queue and audit log, and the six-week dashboard — bilingual EN/AR.
"""
import os
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from functools import wraps

from dotenv import load_dotenv
load_dotenv()

from flask import (Flask, render_template, request, redirect, url_for, flash,
                   abort, session, jsonify)
from flask_login import (LoginManager, login_user, logout_user, login_required,
                         current_user)
from sqlalchemy import or_

from models import (db, D, User, Setting, get_setting, set_setting, Approval,
                    AuditLog, RevenueType, CostCategory, BankAccount,
                    OpeningOverride, CURRENCIES, STATUSES, ST_DRAFT, ST_SUBMITTED,
                    ST_APPROVED, ST_REJECTED, ST_CANCELLED, ST_SETTLED)
import services as svc
import permissions as perms
import i18n
from streams import (STREAMS, STREAM_ORDER, INFLOW_STREAMS, OUTFLOW_STREAMS,
                     WEEKDAYS, stream as get_stream, field_label)


# ============================================================
# Form parsing
# ============================================================

def parse_date(s):
    if not s:
        return None
    try:
        return datetime.strptime(str(s).strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def parse_money(s):
    if s is None or str(s).strip() == "":
        return None
    try:
        return D(str(s).replace(",", "").replace("٬", "").strip())
    except (InvalidOperation, ValueError):
        return None


def parse_int(s, lo=None, hi=None):
    try:
        v = int(str(s).strip())
    except (TypeError, ValueError):
        return None
    if lo is not None and v < lo:
        return None
    if hi is not None and v > hi:
        return None
    return v


def read_field(f, form):
    """Return (value, error_key_or_None) for one declared field."""
    raw = form.get(f["name"], "")
    ft = f["type"]
    req = f.get("required")

    if ft in ("text", "textarea"):
        v = (raw or "").strip() or None
        return (v, "required_field" if req and not v else None)

    if ft == "money":
        v = parse_money(raw)
        if v is None:
            return (None, "required_field" if req else None)
        if v < 0:
            return (None, "negative_amount")
        return (svc.q2(v), None)

    if ft == "date":
        v = parse_date(raw)
        return (v, "required_field" if req and v is None else None)

    if ft == "int":
        v = parse_int(raw, f.get("min"), f.get("max"))
        return (v, "required_field" if req and v is None else None)

    if ft == "pct":
        v = parse_int(raw, 0, 100)
        return (100 if v is None else v, None)

    if ft == "weekday":
        v = parse_int(raw, 0, 6)
        return (v, "required_field" if req and v is None else None)

    if ft == "currency":
        v = (raw or "EGP").upper()
        return (v if v in CURRENCIES else "EGP", None)

    if ft == "direction":
        v = (raw or "out").lower()
        return ("in" if v == "in" else "out", None)

    if ft == "select":
        opts = [o[0] for o in f.get("options", [])]
        v = (raw or "").strip()
        if v not in opts:
            v = opts[0] if opts else None
        return (v, None)

    if ft in ("revenue_type", "cost_category"):
        v = parse_int(raw)
        return (v if v else None, None)

    return ((raw or "").strip() or None, None)


def apply_form(spec, row, form):
    errors = {}
    for f in spec["fields"]:
        v, err = read_field(f, form)
        if err:
            errors[f["name"]] = err
            continue
        setattr(row, f["name"], v)
    if getattr(row, "amount", None) in (None, "", 0) and "amount" not in errors:
        errors["amount"] = "required_field"
    return errors


# ============================================================
# App factory
# ============================================================

def create_app(config=None):
    base = os.path.dirname(os.path.abspath(__file__))
    app = Flask(__name__,
                template_folder=os.path.join(base, "templates"),
                static_folder=os.path.join(base, "static"))
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-me-in-production")

    uri = os.environ.get("DATABASE_URL", "sqlite:///sgcash.db")
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql+psycopg://", 1)
    elif uri.startswith("postgresql://") and "+psycopg" not in uri:
        uri = uri.replace("postgresql://", "postgresql+psycopg://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = uri
    eng = {"pool_pre_ping": True}
    if uri.startswith("postgresql+psycopg://"):
        eng["pool_recycle"] = 300
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = eng
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # --- production hardening ------------------------------------------
    # Render terminates TLS at its proxy, so the app must trust the
    # forwarded scheme and host or every redirect would drop to http.
    app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")
    if os.environ.get("RENDER") or os.environ.get("FORCE_HTTPS") == "1":
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
        app.config.update(SESSION_COOKIE_SECURE=True, PREFERRED_URL_SCHEME="https")
    if app.config["SECRET_KEY"] == "change-me-in-production":
        import logging
        logging.getLogger(__name__).warning(
            "SECRET_KEY is unset - sessions are not secure. Set SECRET_KEY before going live.")

    if config:
        app.config.update(config)

    db.init_app(app)
    with app.app_context():
        try:
            db.create_all()
            svc.ensure_schema()
            perms.seed_matrix()
        except Exception:
            db.session.rollback()

    login = LoginManager(app)
    login.login_view = "login"

    @login.user_loader
    def load_user(uid):
        try:
            return db.session.get(User, int(uid))
        except (TypeError, ValueError):
            return None

    # ---------------- Jinja helpers ----------------
    @app.template_filter("money")
    def _money(v, ccy=""):
        try:
            s = f"{float(v):,.2f}"
        except (TypeError, ValueError):
            return "–"
        return f"{s} {ccy}".strip()

    @app.template_filter("money0")
    def _money0(v, ccy=""):
        try:
            s = f"{float(v):,.0f}"
        except (TypeError, ValueError):
            return "–"
        return f"{s} {ccy}".strip()

    @app.template_filter("pct")
    def _pct(v):
        if v is None:
            return "–"
        try:
            return f"{float(v):,.1f}%"
        except (TypeError, ValueError):
            return "–"

    @app.template_filter("d")
    def _d(v):
        if not v:
            return ""
        try:
            return v.strftime("%d %b %Y")
        except AttributeError:
            return str(v)

    app.jinja_env.globals.update(
        t=i18n.t, lang=i18n.lang, direction=i18n.direction, LANGS=i18n.LANGS,
        today=date.today, STREAMS=STREAMS, STREAM_ORDER=STREAM_ORDER,
        INFLOW_STREAMS=INFLOW_STREAMS, OUTFLOW_STREAMS=OUTFLOW_STREAMS,
        WEEKDAYS=WEEKDAYS, CURRENCIES=CURRENCIES, STATUSES=STATUSES,
        ACTIONS=perms.ACTIONS, ROLES=perms.ROLES,
        field_label=lambda f: field_label(f, i18n.lang()),
        stream_label=lambda k: (STREAMS[k]["ar"] if i18n.lang() == "ar" else STREAMS[k]["en"]),
    )

    @app.context_processor
    def _inject():
        brand = svc.get_brand()
        auth = current_user.is_authenticated
        pending = 0
        if auth and perms.can_approve_any(current_user):
            try:
                pending = Approval.query.filter_by(status="pending").count()
            except Exception:
                pending = 0
        return dict(
            brand=brand, app_version=svc.VERSION, fx=svc.fx_rate(),
            can=(lambda c: perms.has_perm(current_user, c)) if auth else (lambda c: False),
            can_s=(lambda s, a: perms.can(current_user, s, a)) if auth else (lambda s, a: False),
            my_streams=(perms.visible_streams(current_user) if auth else []),
            pending_approvals=pending,
            can_approve_any=(perms.can_approve_any(current_user) if auth else False),
            ROLE_LABEL=(perms.ROLE_LABELS_AR if i18n.lang() == "ar" else perms.ROLE_LABELS),
        )

    def _needs_setup():
        try:
            return User.query.first() is None
        except Exception:
            return False

    @app.before_request
    def _guards():
        ep = request.endpoint or ""
        if ep in perms.OPEN_ENDPOINTS or ep.startswith("static"):
            return
        if _needs_setup():
            return redirect(url_for("setup"))
        cap = ENDPOINT_CAP.get(ep)
        if cap and current_user.is_authenticated and not perms.has_perm(current_user, cap):
            abort(403)

    def who():
        return current_user.display if current_user.is_authenticated else "system"

    def audit(action, target="", detail=""):
        svc.audit(who(), action, target, detail)

    def require(cap):
        def deco(f):
            @wraps(f)
            def w(*a, **k):
                if not perms.has_perm(current_user, cap):
                    abort(403)
                return f(*a, **k)
            return w
        return deco

    # =========================================================
    # Setup / auth / language
    # =========================================================
    @app.route("/setup", methods=["GET", "POST"])
    def setup():
        if User.query.first() is not None:
            return redirect(url_for("login"))
        if request.method == "POST":
            u = (request.form.get("username") or "admin").strip() or "admin"
            p = request.form.get("password") or ""
            if len(p) < 6:
                flash("Choose a password of at least 6 characters.", "danger")
                return render_template("setup.html")
            import seed
            seed.initialise(u, p,
                            org=request.form.get("org_name") or svc.DEFAULT_ORG,
                            lang=request.form.get("lang") or "en",
                            demo=request.form.get("demo") == "1")
            flash("Setup complete — please sign in.", "success")
            return redirect(url_for("login"))
        return render_template("setup.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            u = User.query.filter_by(username=(request.form.get("username") or "").strip()).first()
            if u and u.active and u.check_password(request.form.get("password")):
                login_user(u)
                if u.lang:
                    i18n.set_lang(u.lang)
                svc.audit(u.display, "login", u.username)
                return redirect(request.args.get("next") or url_for("dashboard"))
            flash("Invalid username or password.", "danger")
        return render_template("login.html")

    @app.route("/logout")
    @login_required
    def logout():
        svc.audit(who(), "logout", current_user.username)
        logout_user()
        return redirect(url_for("login"))

    @app.route("/lang/<code>")
    def set_lang(code):
        i18n.set_lang(code)
        if current_user.is_authenticated and code in i18n.LANG_KEYS:
            current_user.lang = code
            db.session.commit()
        return redirect(request.referrer or url_for("dashboard"))

    @app.route("/healthz")
    def healthz():
        return jsonify(status="ok", version=svc.VERSION)

    # =========================================================
    # Dashboard & forecast
    # =========================================================
    @app.route("/")
    @login_required
    def dashboard():
        n = parse_int(request.args.get("weeks")) or svc.setting_int("dashboard_weeks")
        dash = svc.dashboard(max(1, min(26, n)))
        return render_template("dashboard.html", dash=dash, n=n)

    @app.route("/forecast")
    @login_required
    @require("forecast")
    def forecast():
        f = svc.build_forecast()
        return render_template("forecast.html", f=f)

    @app.route("/forecast/week/<week_id>")
    @login_required
    @require("forecast")
    def week_detail(week_id):
        f = svc.build_forecast()
        idx = next((i for i, r in enumerate(f["rows"]) if r["week"]["week_id"] == week_id), None)
        if idx is None:
            abort(404)
        moves = svc.movements_for_week(f, idx)
        return render_template("week_detail.html", f=f, row=f["rows"][idx], moves=moves)

    @app.route("/analysis")
    @login_required
    @require("analysis")
    def analysis():
        f_i = parse_int(request.args.get("from")) or 0
        t_i = parse_int(request.args.get("to"))
        a = svc.analysis(from_index=f_i, to_index=t_i)
        weeks = svc.build_weeks()
        return render_template("analysis.html", a=a, weeks=weeks,
                               f_i=f_i, t_i=(t_i if t_i is not None else len(weeks) - 1))

    @app.route("/trend")
    @login_required
    @require("trend")
    def trend():
        lb = parse_int(request.args.get("lookback")) or svc.setting_int("trend_lookback")
        ah = parse_int(request.args.get("ahead")) or svc.setting_int("trend_project")
        method = request.args.get("method") or svc.setting("trend_method")
        if method not in ("linear", "average"):
            method = "linear"
        tf = svc.trend_forecast(lookback=max(2, min(52, lb)),
                                ahead=max(1, min(52, ah)), method=method)
        return render_template("trend.html", tf=tf, lb=lb, ah=ah, method=method)

    # =========================================================
    # The editable tables (generic over the stream registry)
    # =========================================================
    @app.route("/table/<key>/weekly")
    @login_required
    def table_weekly(key):
        spec = _spec_or_404(key)
        if not perms.can(current_user, key, "view"):
            abort(403)
        if not spec.get("weekly_planner"):
            return redirect(url_for("table_list", key=key))
        n = parse_int(request.args.get("weeks")) or svc.setting_int("horizon_weeks")
        weeks = svc.build_weeks(max(1, min(104, n)))
        plan = svc.weekly_stream(key, weeks)
        return render_template("table_weekly.html", key=key, spec=spec, plan=plan,
                               groups=spec.get("group_options") or [])

    @app.route("/table/<key>")
    @login_required
    def table_list(key):
        spec = _spec_or_404(key)
        if not perms.can(current_user, key, "view"):
            abort(403)
        model = spec["model"]
        q = model.query
        status = request.args.get("status") or ""
        ccy = (request.args.get("ccy") or "").upper()
        term = (request.args.get("q") or "").strip()
        if status in STATUSES:
            q = q.filter(model.status == status)
        if ccy in CURRENCIES:
            q = q.filter(model.currency == ccy)
        if term:
            like = f"%{term}%"
            cols = [getattr(model, f["name"]) for f in spec["fields"]
                    if f["type"] in ("text", "textarea") and hasattr(model, f["name"])]
            cols += [model.ref, model.description, model.notes]
            q = q.filter(or_(*[c.ilike(like) for c in cols if c is not None]))
        order = model.due_date.asc() if hasattr(model, "due_date") else model.id.desc()
        rows = q.order_by(order, model.id.asc()).all()
        totals = {c: sum((D(r.amount) for r in rows if r.currency == c), Decimal("0"))
                  for c in CURRENCIES}
        return render_template("table_list.html", key=key, spec=spec, rows=rows,
                               totals=totals, status=status, ccy=ccy, term=term,
                               refs=_reference_lists())

    @app.route("/table/<key>/new", methods=["GET", "POST"])
    @login_required
    def table_new(key):
        spec = _spec_or_404(key)
        if not perms.can(current_user, key, "enter"):
            abort(403)
        model = spec["model"]
        row = model()
        errors = {}
        if request.method == "POST":
            errors = apply_form(spec, row, request.form)
            if not errors:
                row.status = ST_DRAFT
                row.created_by = who()
                row.updated_by = who()
                db.session.add(row)
                db.session.commit()
                audit(f"{key}_created", row.id, _summary(key, row))
                if request.form.get("and_submit") == "1" and perms.can(current_user, key, "enter"):
                    _submit_row(key, row)
                    flash(i18n.t("submit_for_approval") + " ✓", "success")
                else:
                    flash(i18n.t("saved"), "success")
                return redirect(url_for("table_list", key=key))
        return render_template("table_form.html", key=key, spec=spec, row=row,
                               errors=errors, refs=_reference_lists(), mode="new")

    @app.route("/table/<key>/<int:rid>/edit", methods=["GET", "POST"])
    @login_required
    def table_edit(key, rid):
        spec = _spec_or_404(key)
        model = spec["model"]
        row = db.session.get(model, rid) or abort(404)
        if not perms.can(current_user, key, "view"):
            abort(403)
        editable = perms.can(current_user, key, "edit")
        errors = {}
        if request.method == "POST":
            if not editable:
                abort(403)
            if row.status == ST_APPROVED and not perms.can(current_user, key, "approve"):
                flash("Approved entries can only be changed by an approver.", "danger")
                return redirect(url_for("table_list", key=key))
            before = _summary(key, row)
            errors = apply_form(spec, row, request.form)
            if not errors:
                row.updated_by = who()
                if row.status in (ST_APPROVED, ST_REJECTED):
                    row.status = ST_DRAFT      # a material change needs re-approval
                    row.approved_by = None
                    row.approved_at = None
                db.session.commit()
                audit(f"{key}_updated", row.id, f"{before} → {_summary(key, row)}")
                flash(i18n.t("saved"), "success")
                return redirect(url_for("table_list", key=key))
        return render_template("table_form.html", key=key, spec=spec, row=row,
                               errors=errors, refs=_reference_lists(), mode="edit",
                               editable=editable)

    @app.route("/table/<key>/<int:rid>/delete", methods=["POST"])
    @login_required
    def table_delete(key, rid):
        spec = _spec_or_404(key)
        if not perms.can(current_user, key, "delete"):
            abort(403)
        row = db.session.get(spec["model"], rid) or abort(404)
        detail = _summary(key, row)
        Approval.query.filter_by(stream=key, row_id=rid, status="pending").delete()
        db.session.delete(row)
        db.session.commit()
        audit(f"{key}_deleted", rid, detail)
        flash(i18n.t("delete") + " ✓", "success")
        return redirect(url_for("table_list", key=key))

    @app.route("/table/<key>/<int:rid>/submit", methods=["POST"])
    @login_required
    def table_submit(key, rid):
        spec = _spec_or_404(key)
        if not perms.can(current_user, key, "enter") and not perms.can(current_user, key, "edit"):
            abort(403)
        row = db.session.get(spec["model"], rid) or abort(404)
        _submit_row(key, row)
        flash(i18n.t("submit_for_approval") + " ✓", "success")
        return redirect(request.referrer or url_for("table_list", key=key))

    def _submit_row(key, row):
        row.status = ST_SUBMITTED
        row.reviewed_by = None
        row.reviewed_at = None
        db.session.commit()
        existing = Approval.query.filter_by(stream=key, row_id=row.id, status="pending").first()
        if not existing:
            db.session.add(Approval(
                stream=key, row_id=row.id, kind="entry", summary=_summary(key, row),
                currency=row.currency, amount=row.amount, requester=who(),
                requester_id=(current_user.id if current_user.is_authenticated else None)))
            db.session.commit()
        audit(f"{key}_submitted", row.id, _summary(key, row))

    @app.route("/table/<key>/<int:rid>/decide/<decision>", methods=["POST"])
    @login_required
    def table_decide(key, rid, decision):
        spec = _spec_or_404(key)
        if not perms.can(current_user, key, "approve") or \
                perms.role_key(current_user) not in perms.get_approver_roles() + ["admin"]:
            abort(403)
        if decision not in ("approve", "reject"):
            abort(400)
        row = db.session.get(spec["model"], rid) or abort(404)
        ap = Approval.query.filter_by(stream=key, row_id=rid, status="pending").first()
        if ap and ap.requester_id and ap.requester_id == current_user.id and not current_user.is_admin:
            flash(i18n.t("no_self_approve"), "danger")
            return redirect(request.referrer or url_for("approvals"))
        if row.created_by == who() and not current_user.is_admin:
            flash(i18n.t("no_self_approve"), "danger")
            return redirect(request.referrer or url_for("approvals"))
        row.status = ST_APPROVED if decision == "approve" else ST_REJECTED
        row.reviewed_by = who()
        row.reviewed_at = datetime.now()
        if decision == "approve":
            row.approved_by = who()
            row.approved_at = datetime.now()
        if ap:
            ap.status = "approved" if decision == "approve" else "rejected"
            ap.approver = who()
            ap.decided_at = datetime.now()
            ap.reason = request.form.get("reason")
        db.session.commit()
        audit(f"{key}_{row.status}", rid, _summary(key, row))
        flash(i18n.t("approve" if decision == "approve" else "reject") + " ✓", "success")
        return redirect(request.referrer or url_for("approvals"))

    @app.route("/table/<key>/<int:rid>/settle", methods=["POST"])
    @login_required
    def table_settle(key, rid):
        spec = _spec_or_404(key)
        if not perms.can(current_user, key, "edit"):
            abort(403)
        row = db.session.get(spec["model"], rid) or abort(404)
        row.status = ST_SETTLED if row.status != ST_SETTLED else ST_APPROVED
        row.updated_by = who()
        db.session.commit()
        audit(f"{key}_{row.status}", rid, _summary(key, row))
        return redirect(request.referrer or url_for("table_list", key=key))

    # =========================================================
    # Banks & opening balances
    # =========================================================
    @app.route("/banks", methods=["GET", "POST"])
    @login_required
    @require("banks_view")
    def banks():
        if request.method == "POST":
            if not perms.has_perm(current_user, "banks_edit"):
                abort(403)
            rid = parse_int(request.form.get("id"))
            a = db.session.get(BankAccount, rid) if rid else BankAccount()
            if a is None:
                abort(404)
            a.name = (request.form.get("name") or "").strip()
            a.bank = (request.form.get("bank") or "").strip() or None
            a.account_no = (request.form.get("account_no") or "").strip() or None
            ccy = (request.form.get("currency") or "EGP").upper()
            a.currency = ccy if ccy in CURRENCIES else "EGP"
            a.balance = svc.q2(parse_money(request.form.get("balance")) or 0)
            a.overdraft_limit = svc.q2(parse_money(request.form.get("overdraft_limit")) or 0)
            a.as_at = parse_date(request.form.get("as_at")) or date.today()
            a.include_in_forecast = request.form.get("include_in_forecast") == "1"
            a.notes = (request.form.get("notes") or "").strip() or None
            a.updated_by = who()
            if not a.name:
                flash(i18n.t("required_field"), "danger")
                return redirect(url_for("banks"))
            if not rid:
                db.session.add(a)
            db.session.commit()
            audit("bank_saved", a.id, f"{a.name} {a.currency} {a.balance}")
            flash(i18n.t("saved"), "success")
            return redirect(url_for("banks"))
        rows = BankAccount.query.order_by(BankAccount.currency, BankAccount.name).all()
        tot = svc.bank_opening()
        return render_template("banks.html", rows=rows, tot=tot,
                               eqv=svc.egp_equivalent(tot))

    @app.route("/banks/<int:rid>/delete", methods=["POST"])
    @login_required
    @require("banks_edit")
    def bank_delete(rid):
        a = db.session.get(BankAccount, rid) or abort(404)
        name = a.name
        db.session.delete(a)
        db.session.commit()
        audit("bank_deleted", rid, name)
        return redirect(url_for("banks"))

    @app.route("/opening", methods=["GET", "POST"])
    @login_required
    @require("forecast")
    def opening():
        if request.method == "POST":
            if not perms.has_perm(current_user, "opening_edit"):
                abort(403)
            wid = request.form.get("week_id")
            ccy = (request.form.get("currency") or "").upper()
            if ccy not in CURRENCIES or not wid:
                abort(400)
            if request.form.get("clear") == "1":
                svc.clear_opening_override(wid, ccy)
                audit("opening_cleared", f"{wid}/{ccy}")
            else:
                v = parse_money(request.form.get("opening"))
                if v is None:
                    flash(i18n.t("required_field"), "danger")
                    return redirect(url_for("opening"))
                svc.set_opening_override(wid, ccy, v, who(), request.form.get("reason") or "")
                audit("opening_set", f"{wid}/{ccy}", str(v))
            flash(i18n.t("saved"), "success")
            return redirect(url_for("opening"))
        f = svc.build_forecast()
        return render_template("opening.html", f=f)

    # =========================================================
    # Approvals, delegation, users, audit, settings
    # =========================================================
    @app.route("/approvals")
    @login_required
    @require("approvals")
    def approvals():
        pending = Approval.query.filter_by(status="pending").order_by(Approval.id.desc()).all()
        history = (Approval.query.filter(Approval.status != "pending")
                   .order_by(Approval.id.desc()).limit(100).all())
        rows = {}
        for a in pending:
            spec = STREAMS.get(a.stream)
            if spec:
                rows[a.id] = db.session.get(spec["model"], a.row_id)
        return render_template("approvals.html", pending=pending, history=history, rows=rows)

    @app.route("/admin/delegation", methods=["GET", "POST"])
    @login_required
    @require("access_control")
    def delegation():
        if request.method == "POST":
            changes = 0
            for role in perms.ROLE_KEYS:
                if role == "admin":
                    continue
                for cap in perms.CAP_KEYS:
                    allowed = request.form.get(f"p_{role}_{cap}") == "on"
                    row = db.session.get(__import__("models").RolePermission, (role, cap))
                    if bool(row and row.allowed) != allowed:
                        perms.set_permission(role, cap, allowed)
                        changes += 1
            perms.set_approver_roles(request.form.getlist("approver_roles"))
            audit("delegation_updated", "matrix", f"{changes} change(s)")
            flash(i18n.t("saved"), "success")
            return redirect(url_for("delegation"))
        return render_template("delegation.html", matrix=perms.get_matrix(),
                               caps=perms.CORE_CAPS, cap_labels=(
                                   perms.CAP_LABELS_AR if i18n.lang() == "ar" else perms.CAP_LABELS),
                               approver_roles=perms.get_approver_roles(),
                               stream_cap=perms.stream_cap)

    @app.route("/admin/delegation/reset", methods=["POST"])
    @login_required
    @require("access_control")
    def delegation_reset():
        perms.seed_matrix(force=True)
        audit("delegation_reset", "matrix")
        flash(i18n.t("saved"), "success")
        return redirect(url_for("delegation"))

    @app.route("/admin/users", methods=["GET", "POST"])
    @login_required
    @require("users_admin")
    def users():
        if request.method == "POST":
            act = request.form.get("action")
            if act == "new":
                un = (request.form.get("username") or "").strip()
                pw = request.form.get("password") or ""
                if not un or User.query.filter_by(username=un).first():
                    flash("Username missing or already in use.", "danger")
                elif len(pw) < 6:
                    flash("Password must be at least 6 characters.", "danger")
                else:
                    u = User(username=un, full_name=request.form.get("full_name"),
                             email=(request.form.get("email") or None),
                             role=request.form.get("role", "data_entry"),
                             lang=request.form.get("lang", "en"))
                    u.set_password(pw)
                    db.session.add(u)
                    db.session.commit()
                    audit("user_created", un, f"role={u.role}")
                    flash(i18n.t("saved"), "success")
            elif act == "update":
                u = db.session.get(User, parse_int(request.form.get("id"))) or abort(404)
                new_role = request.form.get("role") or u.role
                if u.role == "admin" and new_role != "admin" and \
                        User.query.filter_by(role="admin").count() <= 1:
                    flash("You cannot remove the only administrator.", "danger")
                    return redirect(url_for("users"))
                old = f"role={u.role}"
                u.full_name = request.form.get("full_name") or u.full_name
                u.email = request.form.get("email") or None
                u.role = new_role
                u.active = request.form.get("active") == "1"
                db.session.commit()
                audit("user_updated", u.username, f"{old} → role={u.role}")
                flash(i18n.t("saved"), "success")
            elif act == "reset":
                u = db.session.get(User, parse_int(request.form.get("id"))) or abort(404)
                pw = request.form.get("password") or ""
                if len(pw) < 6:
                    flash("Password must be at least 6 characters.", "danger")
                else:
                    u.set_password(pw)
                    db.session.commit()
                    audit("user_password_reset", u.username)
                    flash(i18n.t("saved"), "success")
            return redirect(url_for("users"))
        return render_template("users.html", rows=User.query.order_by(User.username).all())

    @app.route("/admin/audit")
    @login_required
    @require("audit_log")
    def audit_view():
        rows = AuditLog.query.order_by(AuditLog.id.desc()).limit(500).all()
        return render_template("audit.html", rows=rows)

    @app.route("/admin/reference", methods=["GET", "POST"])
    @login_required
    @require("reference_data")
    def reference():
        if request.method == "POST":
            kind = request.form.get("kind")
            Model = RevenueType if kind == "revenue" else CostCategory
            rid = parse_int(request.form.get("id"))
            row = db.session.get(Model, rid) if rid else Model()
            if row is None:
                abort(404)
            if request.form.get("remove") == "1" and rid:
                row.active = False
            else:
                row.code = (request.form.get("code") or "").strip().upper()[:30]
                row.name_en = (request.form.get("name_en") or "").strip()
                row.name_ar = (request.form.get("name_ar") or "").strip() or None
                row.active = True
                if kind == "cost":
                    row.group_key = request.form.get("group_key") or "operating"
                if not row.code or not row.name_en:
                    flash(i18n.t("required_field"), "danger")
                    return redirect(url_for("reference"))
                if not rid:
                    db.session.add(row)
            db.session.commit()
            audit("reference_saved", f"{kind}:{row.code}", row.name_en)
            flash(i18n.t("saved"), "success")
            return redirect(url_for("reference"))
        return render_template("reference.html", **_reference_lists(all_rows=True))

    @app.route("/settings", methods=["GET", "POST"])
    @login_required
    @require("settings")
    def settings():
        keys = ["work_week", "week_start", "weekend_rule", "horizon_weeks",
                "dashboard_weeks", "fx_rate", "min_buffer_EGP", "min_buffer_USD",
                "org_name", "product_name", "default_lang", "forecast_start",
                "trend_lookback", "trend_project", "trend_method"]
        if request.method == "POST":
            for k in keys:
                if k in request.form:
                    set_setting(k, (request.form.get(k) or "").strip())
            set_setting("include_pending", "1" if request.form.get("include_pending") == "on" else "0")
            set_setting("apply_certainty", "1" if request.form.get("apply_certainty") == "on" else "0")
            audit("settings_updated", "system")
            flash(i18n.t("saved"), "success")
            return redirect(url_for("settings"))
        vals = {k: svc.setting(k) for k in keys}
        vals["include_pending"] = svc.setting_bool("include_pending")
        vals["apply_certainty"] = svc.setting_bool("apply_certainty")
        return render_template("settings.html", v=vals, work_weeks=svc.WORK_WEEKS)

    # ---------------- errors ----------------
    @app.errorhandler(403)
    def _403(e):
        return render_template("error.html", code=403,
                               msg="You do not have permission for that action."), 403

    @app.errorhandler(404)
    def _404(e):
        return render_template("error.html", code=404, msg="Page not found."), 404

    return app


# ============================================================
# Shared helpers used by the routes
# ============================================================

ENDPOINT_CAP = {
    "dashboard": "dashboard",
    "forecast": "forecast",
    "week_detail": "forecast",
    "analysis": "analysis",
    "trend": "trend",
    "banks": "banks_view",
    "bank_delete": "banks_edit",
    "opening": "forecast",
    "approvals": "approvals",
    "delegation": "access_control",
    "delegation_reset": "access_control",
    "users": "users_admin",
    "audit_view": "audit_log",
    "reference": "reference_data",
    "settings": "settings",
}


def _spec_or_404(key):
    try:
        return get_stream(key)
    except KeyError:
        abort(404)


def _reference_lists(all_rows=False):
    rq = RevenueType.query
    cq = CostCategory.query
    if not all_rows:
        rq = rq.filter_by(active=True)
        cq = cq.filter_by(active=True)
    return {"revenue_types": rq.order_by(RevenueType.sort, RevenueType.name_en).all(),
            "cost_categories": cq.order_by(CostCategory.sort, CostCategory.name_en).all()}


def _summary(key, row):
    spec = STREAMS[key]
    from services import _describe
    return f"{spec['en']}: {_describe(key, row)} — {row.currency} {row.amount}"


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
