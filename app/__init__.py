#  this runs when Python imports the app folder. It's where you 
#create the Flask app, connect SQLAlchemy, and register your 
#routes. Like your app.js in UTRGV Match.
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


#creates an empty SQLAlchemy object
#  "I'm going to have a database."
db = SQLAlchemy()
#function that crates the app
def create_app(config):
    #just creates the Flask app, and __name__ tells Flask where the
    #app lives so it can find the templates and static files.
    app = Flask(__name__)
    # loads the config object 
    #(secret key, database URL, etc.) into the app
    app.config.from_object(config)
    #when the app opens initilaize the db
    # "now connect it to this specific Flask app."
    db.init_app(app)
    # This is what tells SQLAlchemy "hey, this table exists."
    from app.models.hearing import Hearing  # noqa: F401
    from app.models.public_comment import PublicComment  # noqa: F401
    from app.models.hearing_summary import Hearingsummary # noqa: F401
    from app.routes.api import api_bp
    from app.routes.web import web_bp
    #Notice api_bp gets a url_prefix of /api so all API routes 
    #automatically start with /api. web_bp has no prefix so its 
    #routes start from /
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
    return app


