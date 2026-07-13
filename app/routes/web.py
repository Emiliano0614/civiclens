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
from app.auth import login_required, admin_required
from app.services.comment_service import create_comment
from flask import Blueprint, render_template, request, redirect, url_for, session
from app.services.auth_service import verify_login, create_user
from app.models.hearing import Hearing
from app.models.public_comment import PublicComment
from app.models.comment_cluster import CommentCluster
#"web" is the name flask uses to identify this blueprint
#name tells flask ehere the blue print lives so it can resolve the
#paths

web_bp = Blueprint("web",__name__)
#route just displays a page
@web_bp.route("/hearings", methods=["GET"])
def list_hearing():
    hearings = list_hearings()
    return render_template("hearings/list.html", hearings=hearings)





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