from flask import abort, Blueprint, g

from flask_restful import Api, fields, marshal, Resource, reqparse, url_for

from auth import auth
import models


class Username(fields.Raw):
    def format(self, value):
        return value.username


todo_fields = {
    'name': fields.String,
    'creating_user': Username
}


class TodoBase(Resource):
    def __init__(self):
        self.request_parser = reqparse.RequestParser()
        self.request_parser.add_argument(
            'name',
            required=True,
            help='No to do name supplied',
            location=['form', 'json']
        )
        super().__init__()


class TodosList(TodoBase):

    @auth.login_required
    def get(self):
        queryset = models.Todo.select().join(models.User).where(models.User.id == g.user.id)
        todos = [
            marshal(todo, todo_fields) for todo in queryset
        ]
        return {'todos': todos}, 200

    @auth.login_required
    def post(self):
        args = self.request_parser.parse_args()
        todo = models.Todo.create(
            name=args.get('name'),
            creating_user=g.user,
        )
        return {
            'new_todo': marshal(todo, todo_fields),
            'location': url_for('resources.todos.todo', id=todo.id),
        }, 201


class TodoDetail(TodoBase):

    @auth.login_required
    def put(self, id):
        args = self.request_parser.parse_args()
        try:
            todo_record = models.Todo.select().where(models.Todo.id == id).get()
        except models.DoesNotExist:
            abort(404)
        else:
            if g.user == todo_record.creating_user:
                todo_record.name = args.get('name')
                todo_record.save()
                return {
                    'updated_todo': marshal(todo_record, todo_fields),
                    'location': url_for('resources.todos.todo', id=id)
                }, 200
            else:
                return {'error': 'You cannot edit other users todos!'}, 401

    @auth.login_required
    def delete(self, id):
        try:
            todo_record = models.Todo.select().where(models.Todo.id == id).get()
        except models.DoesNotExist:
            abort(404)
        else:
            if g.user == todo_record.creating_user:
                todo_record.delete_instance()
                return '', 204, {'location': url_for('resources.todos.todos')}
            else:
                return {'error': 'You cannot delete other users todos!'}, 401


todos_api = Blueprint('resources.todos', __name__)
api = Api(todos_api)
api.add_resource(
    TodosList,
    '/todos',
    endpoint='todos'
)
api.add_resource(
    TodoDetail,
    '/todos/<int:id>',
    endpoint='todo'
)
