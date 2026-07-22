# returns HTML using render_template(), used when the browser
# navigates to a page like /hearings or /login.
#i need a blue print so that my server dosent crash when 
#app.register_blueprint(api_bp, url_prefix="/api")
# blue print is like a mini  app that groups routes toghther 
#A Blueprint actually holds the routes
from datetime import date as date_type
from app.services.hearing_service import (
    list_hearings,
    create_hearing,
    get_hearing_by_id,
)
from app.auth import login_required, admin_required, get_current_user
from app.services.comment_service import create_comment, get_comment, delete_comment
from flask import Blueprint, render_template, request, redirect, url_for, session, abort
from app.services.auth_service import verify_login, create_user
from app.models.hearing import Hearing
from app.models.public_comment import PublicComment
from app.models.comment_cluster import CommentCluster
from app.services.cluster_orchestrator import get_cluster
from app.services.accountability_orchestrator import get_accountability_summary
from app.services.government_decision_service import get_decision
from app.services.summary_orchestrator import get_summary
from app.services.user_service import get_users_by_ids
#"web" is the name flask uses to identify this blueprint
#name tells flask ehere the blue print lives so it can resolve the
#paths

web_bp = Blueprint("web",__name__)

@web_bp.context_processor
def inject_current_user():
    return {"current_user": get_current_user()}

@web_bp.route("/")
def index():
     return render_template("home.html")

@web_bp.route("/about")
def about():
    return render_template("about.html")


#route just displays a page
@web_bp.route("/hearings", methods=["GET"])
def list_hearing():
    hearings = list_hearings()
    for hearing in hearings:
        hearing.summary = get_summary(hearing.id)
    return render_template("hearings/list.html", hearings=hearings)


@web_bp.route("/hearings/<int:hearing_id>")
def hearing_detail(hearing_id):
    hearing = get_hearing_by_id(hearing_id)
    if hearing is None:
        abort(404)
    comments = get_comment(hearing_id)
    author_ids = [c.author_id for c in comments]
    users = get_users_by_ids(author_ids)
    user_index = {u.id: u for u in users}
    comments_data = [c.to_dict() for c in comments]
    clusters = get_cluster(hearing_id)
    clusters_data = [c.to_dict() for c in clusters]
    summary = get_summary(hearing_id)

    decision =  get_decision(hearing_id)
    accountability = get_accountability_summary(hearing_id)
    return render_template(
        "hearings/detail.html",
        hearing=hearing,
        summary=summary,
        comments=comments,
        comments_data=comments_data,
        clusters=clusters,
        clusters_data=clusters_data,
        comment_error=None,
        decision=decision,
        accountability=accountability,
        user_index = user_index
    )

@web_bp.route("/hearings/<int:hearing_id>/comments", methods=["POST"])
@login_required
def submit_comment(hearing_id):
    hearing = get_hearing_by_id(hearing_id)
    if hearing is None:
        abort(404)
    body = request.form.get("body", "").strip()    
    if not body:
        comments = get_comment(hearing_id)
        author_ids = [c.author_id for c in comments]
        users = get_users_by_ids(author_ids)
        user_index = {u.id: u for u in users}
        comments_data = [c.to_dict() for c in comments]
        clusters = get_cluster(hearing_id)
        clusters_data = [c.to_dict() for c in clusters]
        summary = get_summary(hearing_id)
        decision =  get_decision(hearing_id)
        accountability = get_accountability_summary(hearing_id)
        return render_template(
            "hearings/detail.html",
            hearing=hearing,
            summary=summary,
            comments=comments,
            comments_data=comments_data,
            clusters=clusters,
            clusters_data=clusters_data,
            comment_error="Comment cannot be empty.",
            decision=decision,
            accountability=accountability,
            user_index = user_index
        )
    author_id = session.get("user_id")
    create_comment(body, hearing_id, author_id)
    return redirect(url_for("web.hearing_detail", hearing_id=hearing_id))

@web_bp.route("/hearings/<int:hearing_id>/comments/<int:comment_id>/delete", methods=["POST"])
@login_required
def delete_comment_route(hearing_id, comment_id):
    current_user = get_current_user()
    current_user_id = current_user.id
    is_admin = current_user.is_admin
    try:
        delete_comment(comment_id, current_user_id, is_admin)
    except ValueError as e:
        if str(e) == "comment not found":
            abort(404)
        elif str(e) == "You do not have permission to delete this comment":
            abort(403)
    return redirect(url_for("web.hearing_detail", hearing_id=hearing_id))


@web_bp.route("/hearings/new", methods=["GET", "POST"])
@admin_required
def new_hearing():
    if request.method == "GET":
        return render_template("hearings/new.html", error=None, form_data={})
    title = request.form.get("title", "").strip()
    raw_date = request.form.get("date", "").strip()
    transcript = request.form.get("transcript", "").strip() or None
    agenda = request.form.get("agenda", "").strip() or None
    form_data = {"title": title, "date": raw_date, "transcript": transcript, "agenda": agenda}
    if not title:
        return render_template("hearings/new.html", error="Title is required.", form_data=form_data)
    if not raw_date:
        return render_template("hearings/new.html", error="Date is required.", form_data=form_data)
    try:
        parsed_date = date_type.fromisoformat(raw_date)
    except ValueError:
        return render_template("hearings/new.html", error="Invalid date format.", form_data=form_data)
    hearing = create_hearing(title, parsed_date, transcript=transcript, agenda=agenda)
    return redirect(url_for("web.hearing_detail", hearing_id=hearing.id))

@web_bp.route("/login", methods=["GET","POST"])
def login():
    # if its get just show the empty login form
    if request.method == "GET":
        return render_template("auth/login.html", error=None)
    #else the form was submitted, so process the credentials
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    try:
        user = verify_login(email,password)
    except ValueError:
        # re-renders the same login page, but passes an error message into the template
        return render_template("auth/login.html", error="Invalid email or password.")
    session["user_id"] = user.id
    #for testing purposes redirect to / 
    return redirect("/")

@web_bp.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "GET":
        return render_template("auth/signup.html",error=None)
    email = request.form.get("email","").strip()
    password = request.form.get("password","")
    name = request.form.get("full_name","").strip()
    #checks if all the fields are filled out
    if not name or not email or not password:
        return render_template("auth/signup.html", error="All fields are required.")
    try:
        user = create_user(email,password,name)
    except ValueError:
        return render_template("auth/signup.html", error="An account with that email already exists.")
    session["user_id"] = user.id
    #for testing purposes redirect to / 
    return redirect("/")

@web_bp.route("/logout")
def logout():
    session.pop("user_id", None)
     #for testing purposes redirect to / 
    return redirect("/")