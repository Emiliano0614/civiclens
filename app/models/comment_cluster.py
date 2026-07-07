from app import db
from datetime import datetime, timezone
from app.models.public_comment import PublicComment
class CommentCluster(db.Model):
    __tablename__ = "comment_clusters"
    id = db.Column(db.Integer, primary_key=True)
    #its the topic of the cluster
    name = db.Column(db.Text, nullable=False)
    #is a short sentence that explains how the comments relate
    description = db.Column(db.Text, nullable=False)
    hearing_id = db.Column(db.Integer, db.ForeignKey("hearings.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    def to_dict(self):
        return{
        "id":self.id,
        "name": self.name,
        "description": self.description,
        "hearing_id": self.hearing_id,
        "comment_count": self.comment_count,
        "created_at": self.created_at.isoformat(),
        "updated_at": self.updated_at.isoformat()
        }
    @property
    def comment_count(self):
        #queries public comments gets all the comments that are link to
        #cluster returns how many comments there are 
        return PublicComment.query.filter_by(cluster_id=self.id).count()
