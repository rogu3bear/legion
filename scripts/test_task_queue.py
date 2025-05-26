#!/usr/bin/env python3
"""Test TaskQueue functionality with priority support."""

import sys
from pathlib import Path

# Add project root to path
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))

from legion.core.task_queue import TaskQueue


class MockRedis:
    """Mock Redis implementation for testing TaskQueue."""

    def __init__(self):
        self.lists = {}

    def lpush(self, key, value):
        if key not in self.lists:
            self.lists[key] = []
        self.lists[key].insert(0, value)

    def rpush(self, key, value):
        if key not in self.lists:
            self.lists[key] = []
        self.lists[key].append(value)

    def lpop(self, key):
        if self.lists.get(key):
            return self.lists[key].pop(0)
        return None

    def llen(self, key):
        return len(self.lists.get(key, []))


def test_task_queue():
    """Test TaskQueue priority functionality."""
    redis_mock = MockRedis()
    queue = TaskQueue(redis_mock)
    agent_id = "test_agent"

    print("Testing TaskQueue functionality...")

    # Test enqueuing tasks with different priorities
    queue.enqueue_task(agent_id, {"task": "low_priority"}, "low")
    queue.enqueue_task(agent_id, {"task": "normal_priority"}, "normal")
    queue.enqueue_task(agent_id, {"task": "high_priority"}, "high")

    print("✓ Tasks enqueued with different priorities")

    # Test queue length
    length = queue.get_queue_length(agent_id)
    print(f"✓ Queue length: {length} tasks")

    # Test dequeuing (should return high priority first)
    task1 = queue.dequeue_task(agent_id)
    task2 = queue.dequeue_task(agent_id)
    task3 = queue.dequeue_task(agent_id)

    print(f"✓ First task: {task1}")
    print(f"✓ Second task: {task2}")
    print(f"✓ Third task: {task3}")

    # Verify priority order
    if (task1 and task1.get("task") == "high_priority" and
        task2 and task2.get("task") == "normal_priority" and
        task3 and task3.get("task") == "low_priority"):
        print("✓ Priority ordering works correctly")
        return True
    else:
        print("✗ Priority ordering failed")
        return False


if __name__ == "__main__":
    success = test_task_queue()
    print(f"Test {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)
