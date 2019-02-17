import os

from flask import request, jsonify
from flask_jwt_extended import jwt_required, current_user
from sqlalchemy import desc
from werkzeug.utils import secure_filename

from ecommerce_api.factory import db, app
from file_uploads.models import TagImage
from routes import blueprint
from shared.serializers import get_success_response, get_error_response
from tags.models import Tag
from tags.serializers import TagListSerializer


@blueprint.route('/tags', methods=['GET'])
def list_tags():
    page_size = request.args.get('page_size', 5)
    page = request.args.get('page', 1)
    tags = Tag.query.order_by(desc(Tag.created_at)).paginate(page=page, per_page=page_size)
    return jsonify(TagListSerializer(tags).get_data()), 200


def validate_file_upload(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['png', 'jpeg', 'jpg']


@blueprint.route('/tags', methods=['POST'])
@jwt_required
def create_tag():
    if current_user.is_not_admin():
        return jsonify(get_error_response('Permission denied, you must be admin', status_code=401))

    name = request.form.get('name')
    description = request.form.get('description')

    tag = Tag(name=name, description=description)

    if 'images[]' in request.files:
        for image in request.files.getlist('images[]'):
            if image and validate_file_upload(image.filename):
                filename = secure_filename(image.filename)
                dir_path = app.config['IMAGES_LOCATION']
                dir_path = os.path.join((os.path.join(dir_path, 'tags')))

                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)

                file_path = os.path.join(dir_path, filename)
                image.save(file_path)

                file_path = file_path.replace(app.config['IMAGES_LOCATION'].rsplit(os.sep, 2)[0], '')
                if image.content_length == 0:
                    file_size = image.content_length
                else:
                    file_size = os.stat(file_path).st_size

                ti = TagImage(file_path=file_path, file_name=filename, original_name=image.filename,
                              file_size=file_size)
                tag.images.append(ti)

    db.session.add(tag)
    db.session.commit()

    return get_success_response(data=tag.get_summary(), messages='Tag created successfully')
