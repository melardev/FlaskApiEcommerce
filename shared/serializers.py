from flask import request, jsonify
from flask_sqlalchemy import Pagination


class PageSerializer(object):
    def __init__(self, pagination_obj, **kwargs):
        if type(pagination_obj) != Pagination:
            raise EnvironmentError()
        self.data = {}
        self.items = [resource.get_summary(**kwargs) for resource in pagination_obj.items]
        self.data['total_items_count'] = pagination_obj.total
        self.data['offset'] = (pagination_obj.page - 1) * pagination_obj.per_page
        self.data['requested_page_size'] = pagination_obj.per_page
        self.data['current_page_number'] = pagination_obj.page

        self.data['prev_page_number'] = pagination_obj.prev_num or 1
        self.data['total_pages_count'] = pagination_obj.pages

        self.data['has_next_page'] = pagination_obj.has_next
        self.data['has_prev_page'] = pagination_obj.has_prev

        self.data['next_page_number'] = pagination_obj.next_num or self.data['current_page_number']

        self.data['next_page_url'] = '%s?page=%d&page_size=%d' % (
            request.path, self.data['next_page_number'], self.data['requested_page_size'])

        self.data['prev_page_url'] = '%s?page=%d&page_size=%d' % (
            request.path, self.data['prev_page_number'], self.data['requested_page_size'])

    def get_data(self):
        return {
            'success': True,
            'page_meta': self.data,
            self.resource_name: self.items,
        }


def get_success_response(messages, data=None, status_code=200):
    if type(messages) == list:
        msgs = messages
    elif type(messages) == str:
        msgs = [messages]
    else:
        msgs = []

    response = {
        'success': True,
        'full_messages': msgs
    }

    if data is not None:
        response.update(data)

    return jsonify(response), status_code


def get_error_response(messages, status_code=500):
    if type(messages) == list:
        msgs = messages
    elif type(messages) == str:
        msgs = [messages]
    else:
        msgs = []

    return jsonify({
        'success': False,
        'full_messages': msgs
    }), status_code
