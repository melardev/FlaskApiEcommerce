from flask import jsonify

from ecommerce_api.factory import jwt
from users.models import User


# Using the user_claims_loader, we can specify a method that will be
# called when creating access tokens, and add these claims to the said
# token. This method is passed the identity of who the token is being
# created for, and must return data that is json serializable
# @jwt.user_claims_loader
def add_claims_to_access_token(identity):
    return {
        'user_id': identity.id,
        'username': identity.username,
        'roles': [role.name for role in identity.roles]
    }


def no_jwt_for_protected_endpoint(error_message):
    return jsonify({'success': False, 'full_messages': [error_message]})


# This is called on request, when the user accesses a restricted endpoint with a jwt token
# we have to check if the user_id provided indeed maps to an existing user in the db
# how do you know if user_id is indeed user_id and not username or email? well, it is the value
# that you provided in identity_loader(), that value was issued to the user, now you get it back, we issued the id
# then we have the id back :)
def user_loader(user_id):
    # the user will be now available in current_user
    return User.query.get(user_id)


# This is called when a jwt token is gonna be created,
# you have to pass a json serializable object that will be used as the id of the user(identity)
def identity_loader(user):
    return user.id


def token_revoked():
    return jsonify({'success': False, 'full_messages': ['Revoked token']})


def invalid_token_loader(error_message):
    return jsonify({'success': False, 'full_messages': [error_message]})


# anything this function returns will be available as current_user
# it is called when the request is trying to reach a protected endpoint
jwt.user_loader_callback_loader(user_loader)

jwt.user_identity_loader(identity_loader)
jwt.user_claims_loader(add_claims_to_access_token)


# jwt.unauthorized_loader(no_jwt_for_protected_endpoint)
# jwt.revoked_token_loader(token_revoked)


@jwt.expired_token_loader
def valid_but_expired_token(expired_token):
    token_type = expired_token['type']
    return jsonify({
        'success': False,
        'full_messages': [
            'Token expired'
        ]
    }), 401


def validate_file_upload(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['png', 'jpeg', 'jpg']