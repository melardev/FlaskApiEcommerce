from datetime import datetime

from sqlalchemy.orm import relationship

from ecommerce_api.factory import db


class FileUpload(db.Model):
    __tablename__ = 'file_uploads'
    id = db.Column('id', db.Integer, primary_key=True)
    type = db.Column('type', db.String(15))  # this will be our discriminator

    file_path = db.Column(db.String, nullable=False)
    file_name = db.Column(db.String, nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    original_name = db.Column(db.String, nullable=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'FileUpload'
    }


class TagImage(FileUpload):
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), nullable=True)
    tag = relationship('Tag', backref='images')

    __mapper_args__ = {
        'polymorphic_identity': 'TagImage'
    }


class ProductImage(FileUpload):
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    product = relationship('Product', backref='images')

    __mapper_args__ = {
        'polymorphic_identity': 'ProductImage'
    }


class CategoryImage(FileUpload):
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    category = relationship('Category', backref='images')

    __mapper_args__ = {
        'polymorphic_identity': 'CategoryImage'
    }
