class StrictRedis:
    def __init__(self, decode_responses=True):
        self.decode_responses = decode_responses
        self._zsets = {}
        self._hashes = {}
        self.lists = {}

    # sorted set operations
    def zadd(self, name, mapping):
        z = self._zsets.setdefault(name, {})
        z.update(mapping)

    def zrange(self, name, start, end):
        items = self._zsets.get(name, {})
        sorted_items = sorted(items.items(), key=lambda x: x[1])
        return [k for k, _ in sorted_items][start : end + 1]

    def zremrangebyrank(self, name, start, end):
        items = self._zsets.get(name, {})
        sorted_items = sorted(items.items(), key=lambda x: x[1])
        for k, _ in sorted_items[start : end + 1]:
            items.pop(k, None)

    # hash operations
    def hset(self, name, key=None, value=None, mapping=None):
        h = self._hashes.setdefault(name, {})
        if mapping is not None:
            h.update(mapping)
        else:
            h[key] = value

    def hget(self, name, key):
        return self._hashes.get(name, {}).get(key)

    def hgetall(self, name):
        return dict(self._hashes.get(name, {}))

    def hdel(self, name, key):
        self._hashes.get(name, {}).pop(key, None)

    # list operations
    def rpush(self, name, value):
        self.lists.setdefault(name, []).append(value)

    def pipeline(self):
        return Pipeline(self)

class Pipeline:
    def __init__(self, redis):
        self.redis = redis
        self.commands = []

    def zrange(self, *args):
        self.commands.append(('zrange', args))
        return self

    def zremrangebyrank(self, *args):
        self.commands.append(('zremrangebyrank', args))
        return self

    def execute(self):
        results = []
        for cmd, args in self.commands:
            method = getattr(self.redis, cmd)
            results.append(method(*args))
        self.commands = []
        return results
