import os
import re

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, current_user
from sqlalchemy import desc
from werkzeug.utils import secure_filename

from categories.models import Category
from ecommerce_api.factory import db, app
from file_uploads.models import ProductImage
from products.models import Product
from products.serializers import ProductListSerializer, ProductDetailsSerializer
from routes import blueprint
from shared.database import get_or_create
from shared.security import validate_file_upload
from shared.serializers import get_error_response, get_success_response
from tags.models import Tag

product_blueprint = Blueprint('product', __name__)


@blueprint.route('/products', methods=['GET'])
def list_products():
    page = request.args.get('page', 1)
    page_size = request.args.get('page', 5)
    # products = Product.query.order_by(desc(Product.publish_on)).offset((page - 1) * page_size).limit(page_size).all()
    products = Product.query.order_by(desc(Product.publish_on)).paginate(page=1, per_page=5)
    return jsonify(ProductListSerializer(products).get_data()), 200


@blueprint.route('/products/<product_slug>', methods=['GET'])
def show(product_slug):
    product = Product.query.filter_by(slug=product_slug).first()
    # product = Product.query.filter_by(slug=product_slug).first_or_404()
    return jsonify(ProductDetailsSerializer(product).data), 200


@blueprint.route('/products/by_id/<product_id>', methods=['GET'])
def by_id(product_id):
    product = Product.query.get(product_id)
    # product = Product.query.filter_by(slug=product_slug).first_or_404()
    return jsonify(ProductDetailsSerializer(product).data), 200


@blueprint.route('/products', methods=['POST'])
@jwt_required
def create():
    if current_user.is_not_admin():
        return jsonify(get_error_response('Permission denied, you must be admin', status_code=401))

    product_name = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price')
    stock = request.form.get('stock')
    tags = []
    categories = []

    for header_key in list(request.form.keys()):
        if 'tags[' in header_key:
            name = header_key[header_key.find("[") + 1:header_key.find("]")]
            description = request.form[header_key]
            tags.append(get_or_create(db.session, Tag, {'description': description}, name=name)[0])

        if header_key.startswith('categories['):
            result = re.search('\[(.*?)\]', header_key)
            if len(result.groups()) == 1:
                name = result.group(1)
                description = request.form[header_key]
                categories.append(
                    get_or_create(db.session, Category, {'description': description},
                                  name=name)[0])

    product = Product(name=product_name, description=description, price=price, stock=stock,
                      tags=tags, categories=categories)

    if 'images[]' in request.files:
        for image in request.files.getlist('images[]'):
            if image and validate_file_upload(image.filename):
                filename = secure_filename(image.filename)
                dir_path = app.config['IMAGES_LOCATION']
                dir_path = os.path.join((os.path.join(dir_path, 'products')))

                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)

                file_path = os.path.join(dir_path, filename)
                image.save(file_path)

                file_path = file_path.replace(app.config['IMAGES_LOCATION'].rsplit(os.sep, 2)[0], '')
                if image.content_length == 0:
                    file_size = image.content_length
                else:
                    file_size = os.stat(file_path).st_size

                product_image = ProductImage(file_path=file_path, file_name=filename, original_name=image.filename,
                                             file_size=file_size)
                product.images.append(product_image)

    db.session.add(product)
    db.session.commit()

    response = {'full_messages': ['Product created successfully']}
    response.update(ProductDetailsSerializer(product).data)
    return jsonify(response)


@blueprint.route('/products/<product_slug>', methods=['PUT'])
@jwt_required
def update(product_slug):
    name = request.json.get('name')
    description = request.json.get('description')
    stock = request.json.get('stock')
    price = request.json.get('price')

    if not (name and description and price and stock and price):
        return jsonify(get_error_response('You must provide a name, description, stock and price'))

    product = Product.query.filter_by(slug=product_slug).first()
    if product is None:
        return get_error_response(messages='not found', status_code=404)

    product.name = name
    product.description = description
    product.price = price
    product.body = stock

    tags_input = request.json.get('tags')
    categories_input = request.json.get('categories')
    tags = []
    categories = []
    if categories_input:
        for category in categories_input:
            categories.append(
                get_or_create(db.session, Category, {'description': category.get('description', None)},
                              name=category['name'])[0])

    if tags_input:
        for tag in tags_input:
            tags.append(get_or_create(db.session, Tag, {'description': tag.get('description')}, name=tag['name'])[0])

    product.tags = tags
    product.categories = categories
    db.session.commit()
    response = {'full_messages': ['Product updated successfully']}
    response.update(ProductDetailsSerializer(product).data)
    return jsonify(response)


@blueprint.route('/products/<product_slug>', methods=['DELETE'])
@jwt_required
def destroy(product_slug):
    product = Product.query.filter_by(slug=product_slug).first()
    db.session.delete(product)
    db.session.commit()
    return get_success_response('Product deleted successfully')


@blueprint.route('/products/by_id/<product_id>', methods=['DELETE'])
@jwt_required
def destroy_by_id(product_id):
    product = Product.query.get(product_id).first()
    db.session.delete(product)
    db.session.commit()
    return get_success_response('Product deleted successfully')
