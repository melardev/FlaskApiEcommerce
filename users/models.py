from datetime import datetime

from ecommerce_api.factory import db, bcrypt
from roles.models import users_roles


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))
    first_name = db.Column(db.String(300), nullable=False)
    last_name = db.Column(db.String(300), nullable=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # comments = db.relationship('Comment', foreign_keys='comment.user_id', backref='user', lazy='dynamic')

    roles = db.relationship('Role', secondary=users_roles, backref='users')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def is_password_valid(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def is_admin(self):
        return 'ROLE_ADMIN' in [r.name for r in self.roles]

    def is_not_admin(self):
        return not self.is_admin()
