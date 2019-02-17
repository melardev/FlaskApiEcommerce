from datetime import datetime

from flask_jwt_extended import current_user
from slugify import slugify
from sqlalchemy import event
from sqlalchemy.orm import relationship

from ecommerce_api.factory import db
from categories.models import products_categories
from tags.models import products_tags


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String, index=True, unique=True)
    description = db.Column(db.Text, nullable=False)

    price = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime(), default=datetime.utcnow, index=True, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    publish_on = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    tags = relationship('Tag', secondary=products_tags, backref='products')
    categories = relationship('Category', secondary=products_categories, backref='products')

    comments = relationship('Comment', backref='product', lazy='dynamic')

    def __repr__(self):
        return '<Product %r>' % self.name

    def __str__(self):
        return '<Product {}>'.format(self.name)

    def get_summary(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'stock': self.stock,
            'slug': self.slug,
            'comments_count': self.comments.count(),
            'tags': [{'id': t.id, 'name': t.name} for t in self.tags],
            'categories': [{'id': c.id, 'name': c.name} for c in self.categories],
            'image_urls': [i.file_path for i in self.images]
        }


@event.listens_for(Product.name, 'set')
def receive_set(target, value, oldvalue, initiator):
    target.slug = slugify(unicode(value))
