from app import db
from datetime import datetime, timezone

class AccountabilitySummary(db.Model):
    __tablename__ = "accountability_summaries"

    id = db.Column(db.Integer, primary_key=True)
    #the ai gets all the clusters from that hearing for the alignment 
    hearing_id = db.Column(db.Integer, db.ForeignKey("hearings.id"), nullable=False, unique=True)
    #how the gov decision matches with the clusters/users input
    alignment = db.Column(db.String(20), nullable=False )
    reasoning = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self):
        return{
             "id":self.id,
            "hearing_id": self.hearing_id,
            "alignment": self.alignment,
            "reasoning": self.reasoning,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }