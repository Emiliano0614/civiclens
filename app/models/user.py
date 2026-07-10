from datetime import datetime, timezone
from werkzeug.security import check_password_hash, generate_password_hash

from app import db

ROLES = ("admin", "citizen")

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), unique=True, nullable=False)
    #stores the password hash instead of the actual password for security
    #reasons. The actual password is never stored in the database.
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="citizen")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    #hashes the password and stores it in the password_hash field
    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)
    #hashes the passwoed that its passed then compers that to the 
    #hashed password that is stored in the db
    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
        }