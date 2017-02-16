from argon2 import PasswordHasher
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                          BadSignature, SignatureExpired)
from peewee import *

import config


DATABASE = SqliteDatabase('todos.sqlite')
HASHER = PasswordHasher()


class BaseModel(Model):

    class Meta:
        database = DATABASE


class User(BaseModel):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(null=True)

    @classmethod
    def create_user(cls, u_name, e_mail, p_word, **kwargs):
        try:
            cls.select().where(
                (cls.username == u_name) | (cls.email == e_mail.lower())
            ).get()
        except cls.DoesNotExist:
            user = cls(
                username=u_name,
                email=e_mail
            )
            user.password = user.set_password(p_word)
            user.save()
            return user
        else:
            return None

    @staticmethod
    def set_password(pw):
        password = HASHER.hash(pw)
        return password

    def verify_password(self, password):
        return HASHER.verify(self.password, password)

    @staticmethod
    def verify_auth_token(token):
        serializer = Serializer(config.SECRET_KEY)
        try:
            data = serializer.loads(token)
        except (SignatureExpired, BadSignature):
            return None
        else:
            user = User.get(User.id == data['id'])
            return user

    def generate_auth_token(self, expires=3600):
        serializer = Serializer(config.SECRET_KEY, expires_in=expires)
        return serializer.dumps({'id': self.id})


class Todo(BaseModel):
    name = CharField()
    creating_user = ForeignKeyField(User)


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Todo], safe=True)
    DATABASE.close()
