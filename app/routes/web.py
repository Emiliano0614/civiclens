# returns HTML using render_template(), used when the browser
# navigates to a page like /hearings or /login.
#i need a blue print so that my server dosent crash when 
#app.register_blueprint(api_bp, url_prefix="/api")
# blue print is like a mini  app that groups routes toghther 
#A Blueprint actually holds the routes
from flask import Blueprint
#"web" is the name flask uses to identify this blueprint
#name tells flask ehere the blue print lives so it can resolve the
#paths
web_bp = Blueprint("web",__name__)