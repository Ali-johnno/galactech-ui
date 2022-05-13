from . import db
from werkzeug.security import generate_password_hash

class UserProfile(db.Model):
    
    __tablename__ = 'user_profiles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80),unique=True)
    full_name = db.Column(db.String(255))
    password = db.Column(db.String(255))
    date_of_birth = db.Column(db.Date)
    email = db.Column(db.String(255))
    
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2 support
        except NameError:
            return str(self.id)  # python 3 support

    def __repr__(self):
        return '<User %r>' % (self.username)

    def __init__(self, full_name, username, email, date_of_birth, password):
        self.full_name = full_name
        self.email = email
        self.username = username
        self.date_of_birth = date_of_birth
        self.password = generate_password_hash(password)

