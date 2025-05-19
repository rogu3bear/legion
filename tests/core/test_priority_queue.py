import unittest
from legion.task_queue import Task, TaskQueue

class FakeRedis:
    def __init__(self):
        self.store = {}
        self.zsets = {}
        self.lists = {}
    def set(self, k, v):
        self.store[k] = v
    def get(self, k):
        return self.store.get(k)
    def zadd(self, name, mapping):
        self.zsets.setdefault(name, {}).update(mapping)
    def zrange(self, name, start, end):
        items = sorted(self.zsets.get(name, {}).items(), key=lambda x: x[1])
        return [i[0] for i in items][start : end + 1 if end != -1 else None]
    def zrem(self, name, member):
        self.zsets.get(name, {}).pop(member, None)
    def keys(self, pattern):
        import fnmatch
        return [k for k in self.store if fnmatch.fnmatch(k, pattern)]
    def rpush(self, key, value):
        self.lists.setdefault(key, []).append(value)

class PriorityQueueTests(unittest.TestCase):
    def setUp(self):
        self.redis = FakeRedis()
        self.queue = TaskQueue(host="", port=0)
        self.queue.client = self.redis

    def test_priority_order(self):
        t1 = Task(id="1", agent="a", payload={}, priority=5)
        t2 = Task(id="2", agent="a", payload={}, priority=1)
        self.queue.enqueue(t1)
        self.queue.enqueue(t2)
        out = self.queue.dequeue("a")
        self.assertEqual(out.id, "2")

    def test_retry_and_dead_letter(self):
        t = Task(id="x", agent="a", payload={}, priority=1, max_retries=2)
        self.queue.enqueue(t)
        self.queue.record_failure("x", "boom")
        self.queue.record_failure("x", "boom")
        self.queue.record_failure("x", "boom")
        self.assertIn("x", self.redis.lists.get(self.queue.dead_letter_key, []))

if __name__ == "__main__":
    unittest.main()
