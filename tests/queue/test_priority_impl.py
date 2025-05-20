import unittest
from legion.queue.priority import PriorityQueue
from tests.stubs.fakeredis_stub import StrictRedis


class PriorityQueueImplementationTests(unittest.TestCase):
    def test_dequeue_order(self):
        r = StrictRedis()
        q = PriorityQueue(r)
        q.enqueue({"name": "t1"}, priority=1)
        q.enqueue({"name": "t2"}, priority=5)
        q.enqueue({"name": "t3"}, priority=3)
        order = [q.dequeue()["name"] for _ in range(3)]
        self.assertEqual(order, ["t1", "t3", "t2"])


if __name__ == "__main__":
    unittest.main()
