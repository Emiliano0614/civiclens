from app import db
from app.models.government_decision import GovernmentDecision
from app.services.hearing_service import get_hearing_by_id

def create_or_update_decision(hearing_id, decision_text, decision_date=None):
    hearing = get_hearing_by_id(hearing_id)
    if hearing is None:
        raise ValueError(f"hearing {hearing_id} not found")
    #gets the goverment decision    
    decision = GovernmentDecision.query.filter_by(hearing_id=hearing_id).first()
    #checks if there is one if not create it
    if decision is None:
        #crate a space with hearing id alerady in it
        decision = GovernmentDecision(hearing_id=hearing_id)
        db.session.add(decision)
    decision.decision_text = decision_text
    if decision_date is not None:
        decision.decision_date = decision_date
    db.session.commit()
    return decision

def get_decision(hearing_id):
    decision = GovernmentDecision.query.filter_by(hearing_id=hearing_id).first()
    return decision