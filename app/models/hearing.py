#stores the hearings
# imported from your app/__init__.py where it was already created 
#as db = SQLAlchemy().
from app import db
from datetime import datetime, timezone
from app.models.public_comment import PublicComment
from app.models.comment_cluster import CommentCluster
# db.Model SQLAlchemy provides that turns your Python class into a database 
#table.
class Hearing(db.Model):
    #creates the table and name 
    __tablename__ = "hearings"
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.Text, nullable = False)
    date = db.Column(db.Date, nullable = False)
    transcript = db.Column(db.Text, nullable = True)
    youtube_video_id = db.Column(db.String(50), nullable = True)
    agenda = db.Column(db.Text, nullable = True)
    #lambada is just a way to pas a function that gets called each
    #rime a new record is created
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc) )
    #inorder for the jsonfify to work it needs to turn the python 
    #to a  dic
    def to_dict(self):
        return{
            "id": self.id,
            "title": self.title,
            #since date is a object need to convet it to a string
            "date": self.date.isoformat(),
            "transcript": self.transcript,
            "youtube_video_id": self.youtube_video_id,
            "comment_count": self.comment_count,
            "cluster_count": self.cluster_count,
            "agenda": self.agenda,
            #since its a date/time is a object need to convet it to a string
            "created_at": self.created_at.isoformat()
        }
    #how many commetns are in a hearing
    @property
    def comment_count(self):
        return PublicComment.query.filter_by(hearing_id=self.id).count()

    #how many clsuters are in a hearing
    @property
    def cluster_count(self):
        return CommentCluster.query.filter_by(hearing_id=self.id).count()
