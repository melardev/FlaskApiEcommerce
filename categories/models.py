from datetime import datetime

from slugify import slugify
from sqlalchemy import event

from ecommerce_api.factory import db


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    slug = db.Column(db.String(255), index=True, unique=True)
    description = db.Column(db.String())
    created_at = db.Column(db.DateTime(), default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime())

    def get_summary(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'image_urls': [image.file_path.replace('\\', '/') for image in self.images]
        }

    def __repr__(self):
        return self.name


@event.listens_for(Category.name, 'set')
def receive_set(target, value, oldvalue, initiator):
    target.slug = slugify(unicode(value))


products_categories = \
    db.Table("products_categories",
             db.Column("category_id", db.Integer, db.ForeignKey("categories.id")),
             db.Column("product_id", db.Integer, db.ForeignKey("products.id")))
