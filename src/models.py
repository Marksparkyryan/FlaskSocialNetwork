import datetime

from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import UserMixin
from peewee import *



DATABASE = SqliteDatabase("flasksocial.db")
 

class User(UserMixin, Model):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.datetime.now)
    is_admin = BooleanField(default=False)

    class Meta:
        database = DATABASE
        order_by = ("-joined_at",)

    def get_posts(self):
        return Post.select().where(Post.user == self)

    def get_stream(self):
        return Post.select().where(
            (Post.user << self.following()) |
            (Post.user == self)
        )
    
    def following(self):
        """users that we're following"""
        return (
            User.select().join(
                Relationship, on=Relationship.to_user
            ).where(
                Relationship.from_user == self
            )
        )

    def followers(self):
        """get users following current user"""
        return (
            User.select().join(
                Relationship, on=Relationship.from_user
            ).where(
                Relationship.to_user == self
            )
        )
    
    



    @classmethod
    def create_user(cls, username, email, password, admin=False):
        try:
            with DATABASE.transaction():
                cls.create(
                    username=username,
                    email=email,
                    password=generate_password_hash(password),
                    is_admin=admin
                )
        except IntegrityError:
            pass


class Post(Model):
    timestamp = DateTimeField(default=datetime.datetime.now)
    user = ForeignKeyField(
       model=User,
       backref="posts" 
    )
    content = TextField()

    class Meta:
        database = DATABASE
        order_by = ("-timestamp",)


class Relationship(Model):
    from_user = ForeignKeyField(model=User, backref="relationships")
    to_user = ForeignKeyField(model=User, backref="related_to")

    class Meta:
        database = DATABASE
        indexes = (
            (("from_user", "to_user"), True),
        )


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Post, Relationship], safe=True)
    DATABASE.close()
    