from app.services.summarization_service import summarize_hearing
from app.models.hearing_summary import Hearingsummary
from app import db

def run_summary(hearing_id):
    from app.services.hearing_service import get_hearing_by_id
    hearing = get_hearing_by_id(hearing_id)
    if hearing is None:
        raise ValueError(f"Hearing {hearing_id} not found")
    
    summary_data = summarize_hearing(hearing)

    summary = Hearingsummary.query.filter_by(hearing_id=hearing_id).first()
    if summary is None:
        summary = Hearingsummary(hearing_id=hearing_id)
        db.session.add(summary)

    summary.issue_description = summary_data["issue_description"]
    summary.stakeholders = summary_data["stakeholders"]
    summary.key_arguments = summary_data["key_arguments"]
    summary.community_impact = summary_data["community_impact"]

    db.session.commit()
    return summary