import unittest
import legion.queue.priority as pq

class PriorityInterfaceTests(unittest.TestCase):
    def test_interface(self):
        self.assertTrue(hasattr(pq, "enqueue"))
        self.assertTrue(hasattr(pq, "dequeue"))
        self.assertTrue(hasattr(pq, "retry"))

if __name__ == "__main__":
    unittest.main()
