from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_claims, current_user, jwt_optional
from sqlalchemy import desc

from addresses.models import Address
from comments.models import Comment
from ecommerce_api.factory import db
from orders.models import Order, OrderItem
from orders.serializers import OrderListSerializer
from products.models import Product
from routes import blueprint
from shared.serializers import get_success_response, get_error_response


@blueprint.route('/orders', methods=['GET'])
@jwt_required
def my_orders():
    page_size = request.args.get('page_size', 5)
    page = request.args.get('page', 1)

    claims = get_jwt_claims()
    user_id = claims.get('user_id')

    orders = Order.query.filter_by(user_id=user_id).order_by(desc(Order.created_at)) \
        .paginate(page=page,
                  per_page=page_size)
    return jsonify(OrderListSerializer(orders, include_user=True).get_data()), 200


@blueprint.route('/orders/<order_id>', methods=['GET'])
@jwt_required
def order_details(order_id):
    order = Order.query.get(order_id)
    user = current_user
    if order.user_id is user.id or user.is_admin():
        return jsonify(order.get_summary(include_order_items=True)), 200
    else:
        return get_error_response('Access denied, this does not belong to you', status_code=401)


@blueprint.route('/orders', methods=['POST'])
@jwt_optional
def create_order():
    user = current_user
    # You can not check is user is not None because user is LocalProxy even when no authenticated
    # to check if the user is authenticated we may do hasattr
    user_id = user.id if hasattr(user, 'id') else None

    address_id = request.json.get('address_id', None)

    if address_id is not None:
        # reusing address, the user has to be authenticated and owning that address
        address = Address.query.filter_by(id=address_id, user_id=user_id).first()
        if address is None:
            return get_error_response('Permission Denied, you can not use this address', 401)
    else:
        first_name = request.json.get('first_name', None)
        last_name = request.json.get('last_name', None)
        zip_code = request.json.get('zip_code', None)
        street_address = request.json.get('address', None)
        country = request.json.get('address', None)
        city = request.json.get('address', None)

        if user_id is not None:
            if first_name is None:
                first_name = user.first_name

            if last_name is None:
                last_name = user.last_name

        address = Address(first_name=first_name, last_name=last_name, city=city, country=country,
                          street_address=street_address, zip_code=zip_code, )
        if hasattr(user, 'id'):
            address.user_id = user.id

        db.session.add(address)
        db.session.flush()  # we would need the address.id so let's save the address to the db to have the id

    import faker
    fake = faker.Faker()
    order = Order(order_status=0, tracking_number=fake.uuid4(), address_id=address.id)

    cart_items = request.json.get('cart_items')
    product_ids = [ci['id'] for ci in cart_items]
    products = db.session.query(Product).filter(Product.id.in_(product_ids)).all()
    if len(products) != len(cart_items):
        return get_error_response('Error, make sure all products you want to order are still available')

    for index, product in enumerate(products):
        order.order_items.append(OrderItem(price=product.price,
                                           quantity=cart_items[index]['quantity'], product=product,
                                           name=product.name,
                                           slug=product.slug,
                                           user_id=user_id))

    db.session.add(order)
    db.session.commit()
    return get_success_response('Order created successfully', data=order.get_summary(include_order_items=True),
                                status_code=200)
