'''
import enum
from shared.columns import ColIntEnum

# https://www.michaelcho.me/product/using-python-enums-in-sqlalchemy-models
class OrderStatus(enum.IntEnum):
    processed = 1
    image = 2
    audio = 3
    reply = 4
    unknown = 5
'''
from datetime import datetime

from sqlalchemy.orm import relationship

from ecommerce_api.factory import db

ORDER_STATUS = ['processed', 'delivered', 'in transit', 'shipped']


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    # order_status = db.Column(ColIntEnum(OrderStatus), default=OrderStatus.text)
    order_status = db.Column(db.Integer)
    tracking_number = db.Column(db.String)

    address_id = db.Column(db.Integer, db.ForeignKey('addresses.id'), nullable=False)
    address = relationship('Address', backref='orders', lazy=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    user = relationship('User', backref='orders')

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def get_summary(self, include_order_items=False):
        dto = {
            'id': self.id,
            'order_status': ORDER_STATUS[self.order_status],
            'tracking_number': self.tracking_number,
            # Please notice how we retrieve the count, through len(), instead of count()
            # as we did in Product.get_summary() for comments, why? we declared the association in different places
            'address': self.address.get_summary()
        }

        if include_order_items:
            dto['order_items'] = []
            for oi in self.order_items:
                dto['order_items'].append(oi.get_summary())
        else:
            dto['order_items_count'] = len(self.order_items)

        return dto


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True, nullable=False)
    slug = db.Column(db.String)
    price = db.Column(db.Integer, index=True, nullable=False)
    quantity = db.Column(db.Integer, index=True, nullable=False)

    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    order = relationship('Order', backref='order_items')

    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product = relationship('Product', backref='order_items')

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    user = relationship('User', backref='products_bought')

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def get_summary(self):
        return {
            'name': self.name, 'slug': self.slug,
            'product_id': self.product_id,
            'price': self.price, 'quantity': self.quantity
        }
