from app.models.public_comment import PublicComment
from app import db

def create_comment(body, hearing_id, author_id):
    comment = PublicComment(body=body, hearing_id=hearing_id, author_id=author_id)
    db.session.add(comment)
    db.session.commit()
    return comment
#gets all the comments from that hearing
def get_comment(hearing_id):
    all_comments = PublicComment.query.filter_by(hearing_id=hearing_id).all()
    return all_comments