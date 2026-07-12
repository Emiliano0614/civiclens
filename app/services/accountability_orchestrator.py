from app import db
from app.services.cluster_orchestrator import get_cluster
from app.services.government_decision_service import get_decision
from app.services.summary_orchestrator import get_summary
from app.services.hearing_service import get_hearing_by_id
from app.services.accountability_service import compare_decision_to_clusters
from app.models.accountability_summary import AccountabilitySummary
def run_accountability(hearing_id):
    hearing = get_hearing_by_id(hearing_id)
    if hearing is None:
        raise ValueError(f"hearing {hearing_id} not found")
    decision = get_decision(hearing_id)
    if decision is None:
        raise ValueError(f"decision for hearing {hearing_id} not found")
    clusters = get_cluster(hearing_id)
    if clusters == []:
        raise ValueError(f"clusters for hearing {hearing_id} not found")
    summary = get_summary(hearing_id)
    accountability = compare_decision_to_clusters(
        decision_text=decision.decision_text,
        clusters=[c.to_dict() for c in clusters],
        summary= summary.to_dict() if summary else None
    )
    existing_summary = AccountabilitySummary.query.filter_by(hearing_id=hearing_id).first()
    if existing_summary is None:
        summary_row  = AccountabilitySummary(
            hearing_id=hearing_id,
            alignment=accountability["alignment"],
            reasoning=accountability["reasoning"]
        )
        db.session.add(summary_row )
    else:
        existing_summary.alignment = accountability["alignment"]
        existing_summary.reasoning = accountability["reasoning"]
        summary_row = existing_summary
    db.session.commit()
    return summary_row
def get_accountability_summary(hearing_id):
    summary = AccountabilitySummary.query.filter_by(hearing_id=hearing_id).first()
    return summary