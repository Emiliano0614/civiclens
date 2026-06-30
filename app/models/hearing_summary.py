from app import db
from datetime import datetime, timezone
#splits the summary in 4 filds to make it easier for the front end
class Hearingsummary(db.Model):
    __tablename__ = "hearing_summaries"
    id = db.Column(db.Integer, primary_key=True)
    hearing_id = db.Column(db.Integer, db.ForeignKey("hearings.id"), unique=True, nullable=False)
    issue_description = db.Column(db.Text)
    stakeholders = db.Column(db.Text)
    key_arguments = db.Column(db.Text)
    community_impact = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    def to_dict(self):
        return{
            "id": self.id,
            "hearing_id": self.hearing_id,
            "issue_description": self.issue_description,
            "stakeholders": self.stakeholders,
            "key_arguments": self.key_arguments,
            "community_impact": self.community_impact,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }