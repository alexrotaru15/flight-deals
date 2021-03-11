from flask_login import UserMixin
from sqlalchemy.orm import relationship
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from main import db, app


class Users(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(200), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    home_city = db.Column(db.String(150), nullable=False)
    home_iata = db.Column(db.String(20), nullable=False)
    cities = relationship("Destinations")

    def get_reset_token(self, exp_secs=1800):
        s = Serializer(app.config['SECRET_KEY'], exp_secs)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Users.query.get(user_id)


class Destinations(db.Model):
    __tablename__ = "destinations"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    iata_code = db.Column(db.String(100), nullable=False)
    min_no_days = db.Column(db.Integer, nullable=False)
    max_no_days = db.Column(db.Integer, nullable=False)
    max_price = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
