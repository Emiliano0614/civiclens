from functools import wraps
from flask import session , redirect, url_for, request, jsonify, abort

def get_current_user():
    #get the user_id from the session and return the user object 
    #from the database
    #the user_id is stored in the session when the user logs in
    #Flask automatically writes this into a cookie 
    #The browser automatically sends the cookie back on every request 
    #to your domain, no frontend code needed
    user_id = session.get("user_id")
    if user_id is None:
        return None
    return db_get_user(user_id)

def db_get_user(user_id):
    from app.models.user import User
    return User.query.get(user_id)


def login_required(f):
    @wraps(f)
    #*args and **kwargs means accept whatever arguments the original route function accepts
    def decorated(*args, **kwargs):
        #checks if the user is not logged in
        if get_current_user() is None:
            #if the request looks like ans api and js call not a web call 
            if request.is_json or request.path.startswith("/api/"):
                return jsonify({"error": "Authentication required"}), 401
            #not logged in and the request is a web request, redirect to the login page
            return redirect(url_for("web.login"))
        #If we get here, the user is logged in so finally call the real route 
        #function f, passing through whatever arguments it originally needed, and return its result normally.
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if user is None:
            if request.is_json or request.path.startswith("/api/"):
                return jsonify({"error": "Authentication required"}), 401
            return redirect(url_for("web.login"))
        if not user.is_admin:
            if request.is_json or request.path.startswith("/api/"):
                return jsonify({"error": "Admin access required"}), 403
            abort(403)
        return f(*args, **kwargs)
    return decorated