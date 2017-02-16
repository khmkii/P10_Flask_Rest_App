from flask import abort, Blueprint, json

from flask_restful import Api, fields, marshal, Resource, reqparse


from models import User

user_fields = {
    'username': fields.String,
}


class UserList(Resource):

    def __init__(self):
        self.request_parser = reqparse.RequestParser()
        self.request_parser.add_argument(
            'username',
            required=True,
            help='No username provided',
            location=['form', 'json']
        )
        self.request_parser.add_argument(
            'email',
            required=True,
            help='No email address provided',
            location=['form', 'json']
        )
        self.request_parser.add_argument(
            'password',
            required=True,
            help='No password provided',
            location=['form', 'json'],
        )
        self.request_parser.add_argument(
            'verify_password',
            required=True,
            help='No password verification provided',
            location=['form', 'json']
        )
        super().__init__()

    def post(self):
        args = self.request_parser.parse_args()
        if args.get('password') == args.get('verify_password'):
            user = User.create_user(
                u_name=args.get('username'),
                e_mail=args.get('email'),
                p_word=args.get('password')
            )
            if user:
                return marshal(user, user_fields), 201
            else:
                return {'error': 'A user with that email or username already exists'}, 400
        else:
            return {'error': 'Passwords do not match'}, 400


users_api = Blueprint('resources.users', __name__)
api = Api(users_api)
api.add_resource(
    UserList,
    '/users',
    endpoint='users',
)