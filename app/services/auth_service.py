from app import db
from app.models.user import User

def create_user(email, password, name):
    user = User.query.filter_by(email=email).first()
    if user is not None:
        raise ValueError("User with this email is already in use")
    new_user = User(email=email, name=name)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return new_user

def verify_login(email,password):
    user = User.query.filter_by(email=email).first()
    if user is None:
        raise ValueError("Invalid email or password")
    if user.check_password(password) == False:
        raise ValueError("Invalid email or password")
    return user