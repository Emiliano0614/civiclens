from app.models.hearing import Hearing
from app.services.summary_orchestrator import run_summary
from app import db
#gets all the hearings from the db
def list_hearings():
    #the equivalent of SELECT * FROM hearings
    all_hearings = Hearing.query.all()
    return all_hearings
#creates the hearing to the db
def create_hearing(title, date, transcript=None, agenda=None, youtube_video_id=None):
    #creates a new row in memory
    hearing = Hearing(title=title, date=date, transcript=transcript, agenda=agenda, youtube_video_id=youtube_video_id)
    #adds the new row to the hearing
    db.session.add(hearing)
    #confirms the add
    db.session.commit()
    try:
        run_summary(hearing.id)
    except Exception as e:
        print(f"Summarization failed: {e}")

    #need to return because it needs the newly created id so that 
    #the front end knows what its getting
    return hearing
def get_hearing_by_id(hearing_id):
    #get() is specifically for primary keys only.
    hearing = Hearing.query.get(hearing_id)
    return hearing
