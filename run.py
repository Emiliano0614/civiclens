#the entry point, you run this to start the Flask server. It's 
#like node server.js in your UTRGV Match project.


#Because app/__init__.py is special — when Python sees a folder 
#with an __init__.py, it treats the whole folder as a package.
# So from app import create_app means "from the app package, 
#import create_app" — Python automatically looks in __init__.py 
#for it.
from app import create_app, db
from config import Config
import click
app = create_app(Config)
@app.cli.command("seed-admin")
def seed_admin():
    """Create the admin user (admin@admin.com / admin123)."""
    from app.models.user import User
    db.create_all()
    existing = db.session.query(User).filter_by(email="admin@admin.com").first()
    if existing:
        click.echo("Admin user already exists.")
        return
    user = User(email="admin@admin.com", name="Admin", role="admin")
    user.set_password("admin123")
    db.session.add(user)
    db.session.commit()
    click.echo("Admin user created: admin@admin.com / admin123")


@app.cli.command("sync-youtube")
def sync_youtube():
    """Sync hearings from YouTube channel."""
    from app.services.youtube_sync import sync_hidalgo_videos
    sync_hidalgo_videos()


if __name__ == "__main__":
    app.run()