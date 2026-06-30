#stores the commetns
# imported from your app/__init__.py where it was already created 
#as db = SQLAlchemy().
from app import db
from datetime import datetime, timezone
class PublicComment(db.Model):
    #table name 
    __tablename__ = "public_comments"
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    #"hearings.id" is just telling SQLAlchemy the table name. It looks it up in the database directly
    hearing_id = db.Column(db.Integer, db.ForeignKey("hearings.id"),nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    #inorder for the jsonfify to work it needs to turn the python 
    #to a  dic
    def to_dict(self):
        return{
            "id": self.id,
            "body": self.body,
            "created_at": self.created_at.isoformat(),
            "hearing_id": self.hearing_id
        }