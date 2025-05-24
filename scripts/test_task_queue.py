import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from legion.core.task_queue import TaskQueue


class MemoryRedis:
    def __init__(self) -> None:
        self.lists = {}

    def lpush(self, key, value):
        self.lists.setdefault(key, []).insert(0, value)

    def rpush(self, key, value):
        self.lists.setdefault(key, []).append(value)

    def lpop(self, key):
        lst = self.lists.get(key)
        if lst:
            return lst.pop(0)
        return None

    def llen(self, key):
        return len(self.lists.get(key, []))


def main() -> None:
    r = MemoryRedis()
    q = TaskQueue(r)
    q.enqueue_task("agent1", {"t": 1}, priority="normal")
    q.enqueue_task("agent1", {"t": 2}, priority="high")
    q.enqueue_task("agent1", {"t": 3}, priority="low")
    q.enqueue_task("agent1", {"t": 4}, priority="high")

    assert q.get_queue_length("agent1") == 4
    assert q.dequeue_task("agent1")["t"] == 2
    assert q.dequeue_task("agent1")["t"] == 4
    assert q.dequeue_task("agent1")["t"] == 1
    assert q.dequeue_task("agent1")["t"] == 3
    assert q.get_queue_length("agent1") == 0
    print("task queue test: PASS")


if __name__ == "__main__":
    main()


