

class ChannelBackend(object):

    def get(self, id):
        raise NotImplementedError

    def set(self, item, timeout=None):
        raise NotImplementedError

    def get_many(self, keys):
        raise NotImplementedError

    def delete_many(self, keys):
        raise NotImplementedError
