from base64 import b64encode
import sys
import os
import json
from peewee import SqliteDatabase
from playhouse.test_utils import test_database
import unittest

sys.path.insert(0, '../')

import models
import todo_app


class ResourceTest(unittest.TestCase):
    def setUp(self):
        self.db_fd = SqliteDatabase(":memory:")
        todo_app.this_app.config['DATABASE'] = self.db_fd
        todo_app.this_app.config['TESTING'] = True
        self.app = todo_app.this_app.test_client()
        self.user_data = {
            'username': 'test_user',
            'email': 'test@email.com',
            'password': 'password',
            'verify_password': 'password'
        }


class TodoResourceTest(ResourceTest):

    def setUp(self):
        self.root_url = '/api/v1'
        super().setUp()

    def test_get_todos_protected(self):
        path = self.root_url + '/todos'
        resp = self.app.get(path)
        self.assertEqual(resp.status_code, 401)

    def test_post_todos_protected(self):
        path = self.root_url + '/todos'
        resp = self.app.post(path)
        self.assertEqual(resp.status_code, 401)

    def test_put_todos_protected(self):
        path = self.root_url + '/todos/1'
        resp = self.app.put(path)
        self.assertEqual(resp.status_code, 401)

    def test_todo_delete_protected(self):
        path = self.root_url + '/todos/1'
        resp = self.app.delete(path)
        self.assertEqual(resp.status_code, 401)

    def test_can_post_a_todo_and_get_it_back(self):
        with test_database(self.db_fd, models=(models.User, models.Todo)):
            user = models.User.create_user(
                'test_user',
                'email@test.com',
                'password',
            )
            user.save()
            path = self.root_url + '/todos'
            auth_payload = '{0}:{1}'.format(
                    self.user_data['username'],
                    self.user_data['password']
            )
            headers = {
                'Authorization': 'Basic {}'.format(
                    b64encode(
                        bytes(auth_payload, encoding='ascii')
                    ).decode('ascii')
                ),
            }
            resp = self.app.post(
                path,
                headers=headers,
                data={
                    'name': 'test the application',
                },
            )
            returned_creating_user_data = json.loads(resp.data.decode())['new_todo']['creating_user']
            self.assertEqual(resp.status, '201 CREATED')
            self.assertEqual(returned_creating_user_data, user.username)
            resp = self.app.get(
                path,
                headers=headers,
            )
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(
                json.loads(resp.data.decode())['todos'][0]['name'],
                'test the application',
            )
            resp = self.app.delete(
                path + '/1',
                headers=headers,
            )
            self.assertEqual(resp.status_code, 204)


class UserResourceTest(ResourceTest):

    def setUp(self):
        self.root_url = 'api/v1/users'
        super().setUp()

    def test_bad_request_post_users(self):
        resp = self.app.post(
            self.root_url,
            data={}
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("No username provided", str(resp.data, encoding='utf-8'))

    def test_can_create_user(self):
        with test_database(self.db_fd, models=[models.User,]):
            resp = self.app.post(
                self.root_url,
                data=self.user_data
            )
            self.assertEqual(resp.status_code, 201)

    def test_user_can_generate_token(self):
        with test_database(self.db_fd, models=(models.User, )):
            user = models.User.create_user(
                'test_user',
                'email@test.com',
                'password',
            )
            user.save()
            path = self.root_url + '/token'
            auth_payload = '{0}:{1}'.format(
                    self.user_data['username'],
                    self.user_data['password']
            )
            resp = self.app.get(
                path,
                headers={
                    'Authorization': 'Basic {}'.format(
                        b64encode(
                            bytes(auth_payload, encoding='ascii')
                        ).decode('ascii')
                    ),
                })
            # import pdb
            # pdb.set_trace()
            self.assertEqual(resp.status_code, 200)
            returned_token = json.loads(resp.data.decode())['token']
            user_token = user.generate_auth_token().decode()
            self.assertEqual(returned_token, user_token)


if __name__ == '__main__':
    unittest.main()
