from sqlalchemy.orm import synonym
from werkzeug import check_password_hash, generate_password_hash

from flaskr import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), default='', nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    uuid = db.Column(db.String(100), unique=True, nullable=False)
    sex = db.Column(db.String(100), unique=True, nullable=False)
    age = db.Column(db.String(100), unique=True, nullable=False)
    level = db.Column(db.String(100), unique=True, nullable=False)
    _password = db.Column('password', db.String(100), nullable=False)

    def _get_password(self):
        return self._password
    def _set_password(self, password):
        if password:
            password = password.strip()
        self._password = generate_password_hash(password)
    password_descriptor = property(_get_password, _set_password)
    password = synonym('_password', descriptor=password_descriptor)

    def check_password(self, password):
        password = password.strip()
        if not password:
            return False
        return check_password_hash(self.password, password)

    @classmethod
    def authenticate(cls, query, email, password):
        user = query(cls).filter(cls.email==email).first()
        if user is None:
            return None, False
        return user, user.check_password(password)

    def __repr__(self):
        return u'<User id={self.id} email={self.email!r}>'.format(
                self=self)

def init():
    db.create_all()

class Machine(db.Model):
    __tablename__ = 'machines'

    id      = db.Column(db.Integer, primary_key=True)
    name    = db.Column(db.String)
    display = db.Column(db.String)

class Result(db.Model):
    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.String(100), unique=True, nullable=False)
    counted_at = db.Column(db.TIMESTAMP, unique=False, nullable=False)

class AccessLog(db.Model):
    __tablename__ = 'access_logs'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(100), unique=True, nullable=False)
    entered_at = db.Column(db.TIMESTAMP, unique=False)
    exited_at = db.Column(db.TIMESTAMP, unique=False)

class MachineLog(db.Model):
    __tablename__ = 'machine_logs'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(100), unique=True, nullable=False)
    machine_id = db.Column(db.Integer, unique=True, nullable=False)
    entered_at = db.Column(db.TIMESTAMP, unique=False)
