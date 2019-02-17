from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_optional, get_jwt_identity

from ecommerce_api.factory import db, bcrypt
from roles.models import Role
from routes import blueprint
from shared.serializers import get_success_response
from users.models import User


@blueprint.route('/users', methods=['POST'])
def register():
    first_name = request.json.get('first_name', None)
    last_name = request.json.get('last_name', None)
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    email = request.json.get('email', None)
    role = db.session.query(Role).filter_by(name='ROLE_USER').first()
    db.session.add(
        User(first_name=first_name, last_name=last_name, username=username,
             password=bcrypt.generate_password_hash(password).decode('utf-8'), roles=[role], email=email)
    )
    db.session.commit()
    return get_success_response('User registered successfully')


@jwt_optional
def partially_protected():
    # If no JWT is sent in with the request, get_jwt_identity()
    # will return None
    current_user = get_jwt_identity()
    if current_user:
        return jsonify(logged_in_as=current_user), 200
    else:
        return jsonify(loggeed_in_as='anonymous user'), 200


@blueprint.route('/users/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if username is None:
        return jsonify({"msg": "You must supply a username"}), 400
    if password is None:
        return jsonify({"msg": "Missing password parameter"}), 400

    user = User.query.filter_by(username=username).first()

    if user is None or not user.is_password_valid(str(password)):
        return jsonify({"msg": ""}), 401

    # Identity can be any data that is json serializable
    access_token = create_access_token(identity=user)

    return jsonify({
        'success': True,
        'user': {
            'username': user.username, 'id': user.id,
            'roles': [role.name for role in user.roles],
            'token': access_token}
    }), 200
