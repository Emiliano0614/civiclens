#the entry point, you run this to start the Flask server. It's 
#like node server.js in your UTRGV Match project.


#Because app/__init__.py is special — when Python sees a folder 
#with an __init__.py, it treats the whole folder as a package.
# So from app import create_app means "from the app package, 
#import create_app" — Python automatically looks in __init__.py 
#for it.
from app import create_app, db
from config import Config

app = create_app(Config)
with app.app_context():
    db.create_all()
app.run(debug=True)