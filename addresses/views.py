from flask import request, jsonify
from flask_jwt_extended import current_user, jwt_required, get_jwt_identity
from sqlalchemy import desc

from addresses.models import Address
from addresses.serializers import AddressListSerializer
from ecommerce_api.factory import db
from routes import blueprint
from shared.serializers import get_success_response


@blueprint.route('/users/addresses', methods=['GET'])
@jwt_required
def list_addresses():
    page_size = request.args.get('page_size', 5)
    page = request.args.get('page', 1)

    user_id = get_jwt_identity()
    addresses = Address.query.filter_by(user_id=user_id).order_by(desc(Address.created_at)) \
        .paginate(page=page, per_page=page_size)
    return jsonify(AddressListSerializer(addresses, include_user=False).get_data()), 200


@blueprint.route('/users/addresses', methods=['POST'])
@jwt_required
def created_address():
    first_name = request.json.get('first_name')
    last_name = request.json.get('last_name')
    zip_code = request.json.get('zip_code')
    phone_number = request.json.get('phone_number')
    city = request.json.get('city')
    country = request.json.get('country')
    street_address = request.json.get('address')

    # Method 1 of retrieving the user_id when using flask-jwt-extended
    # claims = get_jwt_claims()
    # user_id = claims.get('user_id')

    # Method 2; Method 3 is get_jwt_identity()
    user_id = current_user.id

    address = Address(first_name=first_name, last_name=last_name, zip_code=zip_code, phone_number=phone_number,
                      street_address=street_address, user_id=user_id, city=city, country=country)

    db.session.add(address)
    db.session.commit()

    return get_success_response(data=address.get_summary(), messages='Address created successfully')
