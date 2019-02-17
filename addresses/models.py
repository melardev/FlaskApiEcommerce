from datetime import datetime

from sqlalchemy.orm import relationship

from ecommerce_api.factory import db


class Address(db.Model):
    __tablename__ = 'addresses'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    city = db.Column(db.String, nullable=False)
    country = db.Column(db.String, nullable=False)
    zip_code = db.Column(db.String, nullable=False)
    street_address = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String, nullable=True)  # nullable because I have not implemented it

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    user = relationship('User', backref='addresses')

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_summary(self, include_user=False):
        data = {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'address': self.street_address,
            'zip_code': self.zip_code,
            'city': self.city,
            'country': self.country,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

        if include_user:
            data['user'] = {'id': self.user_id, 'username': self.user.username}

        return data
