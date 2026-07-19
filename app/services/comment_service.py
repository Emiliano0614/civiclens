from app.models.public_comment import PublicComment
from app import db

def create_comment(body, hearing_id, author_id):
    comment = PublicComment(body=body, hearing_id=hearing_id, author_id=author_id)
    db.session.add(comment)
    db.session.commit()
    return comment
#gets all the comments from that hearing
def get_comment(hearing_id):
    all_comments = PublicComment.query.filter_by(hearing_id=hearing_id).order_by(PublicComment.created_at).all()
    return all_comments


def delete_comment(comment_id, current_user_id, is_admin):
    comment = PublicComment.query.get(comment_id)
    if comment is None:
        raise ValueError("comment not found")
    if comment.author_id != current_user_id and not is_admin:
        raise ValueError("You do not have permission to delete this comment")
    db.session.delete(comment)
    db.session.commit()