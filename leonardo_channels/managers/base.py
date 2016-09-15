
import logging
from .backends.cache import cache

LOG = logging.getLogger(__name__)


class BaseManager(object):

    """Simple manager util for storing data related to the group

    store informations in free keys

    name + self.scope + object.id = object
    name + self.scope + count = count
    name + self.scope + all = all[object]
    """

    CACHE_KEY = '{0}.{1}'
    CACHE_COUNT_KEY = '{0}.count'
    CACHE_ALL_KEY = '{0}.all'

    @property
    def db(self):
        """return store backend
        """
        return cache

    def __init__(self, name=None, scope=None, *args, **kwargs):
        self.name = name or self.name
        self.scope = scope or self.scope

        self.clear()

    def get(self, id):
        """return user if exists
        """

        return self.db.get(self.get_item_cache_key(id))

    def clear(self):
        """clear all cache keys
        """

        # this call freeze django start
        # keys = [self.get_item_cache_key(item.id)
        #         for item in self.all()]

        keys = [self.get_all_cache_key(),
                self.get_cache_count_key()]

        return self.db.delete_many(keys)

    def count(self):
        """return count of users
        """

        count = self.db.get(self.get_cache_count_key())

        return count if count else 0

    def all(self):
        """return list of connected users
        """

        items = self.db.get(self.get_all_cache_key())

        return items if items else []

    def add(self, item):
        """Add new user to the group
        """

        # we cant clear this after restart now
        # saved_item = self.db.get(self.get_item_cache_key(item.id))
        # if not saved_item:

        self.db.set(self.get_item_cache_key(item.id), item, None)

        # incerement count because standard cache does not support wildcard
        count = self.db.get(self.get_cache_count_key())

        if not count:
            count = 1
        else:
            count += 1

        self.db.set(self.get_cache_count_key(), count, None)

        all = self.all()

        all += [item]

        self.db.set(self.get_all_cache_key(), all, None)

    def delete(self, id):
        """delete user from cache
        """

        # delete single object
        self.db.delete(self.get_item_cache_key(id))

        # update all
        items = [item for item in self.all() if item.id != id]

        self.db.set(self.get_all_cache_key(), items, None)

        count = self.db.get(self.get_cache_count_key())

        if count:
            count -= 1
            self.db.set(self.get_cache_count_key(), count, None)

    def get_cache_key(self):
        return self.CACHE_KEY.format(self.name, self.scope)

    def get_cache_count_key(self):
        return self.CACHE_COUNT_KEY.format(self.get_cache_key())

    def get_item_cache_key(self, id):
        """return unique cache key
        """
        return '%s.%s' % (self.get_cache_key(), id)

    def get_all_cache_key(self):
        """return unique cache key
        """
        return self.CACHE_ALL_KEY.format(self.get_cache_key())

    _instance = None

    def __new__(cls, *args, **kwargs):
        """A singleton implementation of Manager. There can be only one.
        """
        if not cls._instance:
            cls._instance = super(BaseManager, cls).__new__(
                cls, *args, **kwargs)
        return cls._instance
