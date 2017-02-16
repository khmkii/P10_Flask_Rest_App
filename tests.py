from peewee import SqliteDatabase
from playhouse.test_utils import test_database
import unittest

import models

test_db = SqliteDatabase(':memory:')


class DataBaseModelTests(unittest.TestCase):

    def setUp(self):
        self.username = 'test_user'
        self.email = 'test@email.com'
        self.password = 'test_password'
        self.name = 'test_todo'

    def create_test_user(self):
        return models.User.create_user(
            self.username,
            self.email,
            self.password,
        )

    def create_test_todo(self):
        return models.Todo.create(
            name=self.name,
            creating_user=1
        )

    def test_user_database_operations(self):
        with test_database(db=test_db, models=(models.User,)):
            self.create_test_user()
            user = models.User.get(models.User.username == self.username)
            self.assertEqual(user.username, self.username)
            self.assertTrue(
                user.verify_password(self.password)
            )
            user_again = self.create_test_user()
            self.assertFalse(user_again)

    def test_todo_database_operations(self):
        with test_database(db=test_db, models=(models.Todo,)):
            todo = self.create_test_todo()
            self.assertEqual(todo.name, self.name)


if __name__ == '__main__':
    unittest.main()
