import os

from flask import jsonify, send_from_directory

from ecommerce_api.factory import app


@app.route("/routes")
def site_map():
    links = []
    # for rule in app.url_map.iter_rules():
    for rule in app.url_map._rules:
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        links.append({'ulr': rule.rule, 'view': rule.endpoint})
    return jsonify(links), 200


# @app.route('/api/images/<path:path>')
def send_js(path):
    basedir = os.path.join(os.path.realpath(os.getcwd()), 'static', 'bellerin.png')
    if os.path.exists(basedir):
        return app.send_static_file(basedir)
    return send_from_directory('images', path)
