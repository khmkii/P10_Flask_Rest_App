from flask import Flask, g, jsonify, render_template


from auth import auth
import config
import models
from resources.users import users_api
from resources.todos import todos_api

this_app = Flask(__name__)
this_app.register_blueprint(users_api, url_prefix='/api/v1')
this_app.register_blueprint(todos_api, url_prefix='/api/v1')


@this_app.route('/')
def my_todos():
    return render_template(template_name_or_list='index.html')


@this_app.route('/api/v1/users/token', methods=['GET'])
@auth.login_required
def generate_authentication_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


if __name__ == '__main__':
    models.initialize()
    this_app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
