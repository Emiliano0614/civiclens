 #given a list of author ids (possibly with duplicates), fetch 
 #the actual User row for each unique id that shows up in that 
 #list, in a single database round-trip.
from app.models.user import User

def get_users_by_ids(user_ids):
    #User.id.in_(user_ids) "give me every User row where the
    #id column's value shows up anywhere inside this list.
    return User.query.filter(User.id.in_(user_ids)).all()