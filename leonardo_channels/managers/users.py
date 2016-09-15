from .base import BaseManager


class UserManager(BaseManager):

    scope = 'users'

users = UserManager('widgets.content')
