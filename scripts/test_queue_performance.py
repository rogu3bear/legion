#!/usr/bin/env python3
"""Performance test for optimized TaskQueue implementation."""

import sys
import time
import uuid
from pathlib import Path

# Add project root to path
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))

from legion.task_queue import Task, TaskQueue


class MockRedis:
    """Mock Redis implementation for testing TaskQueue performance."""

    def __init__(self):
        self.data = {}
        self.sorted_sets = {}

    def set(self, key, value):
        self.data[key] = value

    def get(self, key):
        return self.data.get(key)

    def delete(self, key):
        self.data.pop(key, None)

    def keys(self, pattern):
        if pattern == "task:*":
            return [k for k in self.data.keys() if k.startswith("task:") and ":retry_count" not in k and ":error_log" not in k]
        return []

    def zadd(self, key, mapping):
        if key not in self.sorted_sets:
            self.sorted_sets[key] = []
        for member, score in mapping.items():
            # Remove existing entry if present
            self.sorted_sets[key] = [(m, s) for m, s in self.sorted_sets[key] if m != member]
            # Add new entry
            self.sorted_sets[key].append((member, score))
            # Keep sorted by score
            self.sorted_sets[key].sort(key=lambda x: x[1])

    def zrange(self, key, start, end):
        if key not in self.sorted_sets:
            return []
        items = self.sorted_sets[key]
        if end == -1:
            return [item[0] for item in items[start:]]
        else:
            return [item[0] for item in items[start:end+1]]

    def zrem(self, key, member):
        if key in self.sorted_sets:
            self.sorted_sets[key] = [(m, s) for m, s in self.sorted_sets[key] if m != member]

    def zcard(self, key):
        return len(self.sorted_sets.get(key, []))

    def rpush(self, key, value):
        if key not in self.data:
            self.data[key] = []
        self.data[key].append(value)

    def pipeline(self):
        return MockPipeline(self)


class MockPipeline:
    def __init__(self, redis_mock):
        self.redis = redis_mock
        self.commands = []

    def get(self, key):
        self.commands.append(('get', key))
        return self

    def execute(self):
        results = []
        for cmd, key in self.commands:
            if cmd == 'get':
                results.append(self.redis.get(key))
        self.commands = []
        return results


def test_queue_performance():
    """Test TaskQueue performance with optimizations."""
    print("Testing TaskQueue Performance Optimizations")
    print("=" * 50)

    # Create mock Redis for testing
    redis_mock = MockRedis()
    queue = TaskQueue()
    queue.client = redis_mock  # Use mock instead of real Redis

    # Test parameters
    num_agents = 5
    tasks_per_agent = 100
    total_tasks = num_agents * tasks_per_agent

    print(f"Creating {total_tasks} tasks across {num_agents} agents...")

    # Enqueue tasks
    start_time = time.time()
    for agent_id in range(num_agents):
        agent_name = f"agent_{agent_id}"
        for task_id in range(tasks_per_agent):
            task = Task(
                id=str(uuid.uuid4()),
                agent=agent_name,
                payload={"task_number": task_id},
                priority=task_id % 5,  # Vary priorities 0-4
            )
            queue.enqueue(task)

    enqueue_time = time.time() - start_time
    print(f"✓ Enqueued {total_tasks} tasks in {enqueue_time:.3f}s ({total_tasks/enqueue_time:.1f} tasks/sec)")

    # Test agent-specific queue lengths
    print("\nAgent Queue Lengths:")
    for agent_id in range(num_agents):
        agent_name = f"agent_{agent_id}"
        length = queue.get_agent_queue_length(agent_name)
        print(f"  {agent_name}: {length} tasks")

    # Test agent-specific queue stats
    print("\nAgent Queue Statistics:")
    for agent_id in range(min(3, num_agents)):  # Show first 3 agents
        agent_name = f"agent_{agent_id}"
        stats = queue.get_agent_queue_stats(agent_name)
        print(f"  {agent_name}: {stats}")

    # Test dequeue performance
    print(f"\nDequeuing tasks for agent_0...")
    start_time = time.time()
    dequeued_count = 0
    
    while True:
        task = queue.dequeue("agent_0")
        if task is None:
            break
        dequeued_count += 1
        if dequeued_count >= 10:  # Dequeue first 10 tasks
            break

    dequeue_time = time.time() - start_time
    print(f"✓ Dequeued {dequeued_count} tasks in {dequeue_time:.3f}s ({dequeued_count/dequeue_time:.1f} tasks/sec)")

    # Test queue summary performance
    start_time = time.time()
    summary = queue.summary()
    summary_time = time.time() - start_time
    print(f"✓ Generated queue summary in {summary_time:.3f}s: {summary}")

    # Test cleanup performance (simulate old completed tasks)
    print("\nTesting cleanup performance...")
    
    # Mark some tasks as completed with old timestamps
    old_time = time.time() - (25 * 3600)  # 25 hours ago
    completed_tasks = 0
    
    for key in list(redis_mock.data.keys()):
        if key.startswith("task:") and ":retry_count" not in key and ":error_log" not in key:
            task_data = redis_mock.get(key)
            if task_data and completed_tasks < 20:  # Mark first 20 as completed
                import json
                data = json.loads(task_data)
                data["state"] = "completed"
                data["available_at"] = old_time
                redis_mock.set(key, json.dumps(data))
                completed_tasks += 1

    start_time = time.time()
    cleaned = queue.cleanup_completed_tasks(max_age_hours=24)
    cleanup_time = time.time() - start_time
    print(f"✓ Cleaned up {cleaned} old tasks in {cleanup_time:.3f}s")

    print("\nPerformance Test Summary:")
    print(f"  Enqueue Rate: {total_tasks/enqueue_time:.1f} tasks/sec")
    print(f"  Dequeue Rate: {dequeued_count/dequeue_time:.1f} tasks/sec")
    print(f"  Summary Generation: {summary_time:.3f}s")
    print(f"  Cleanup Rate: {cleaned/cleanup_time:.1f} tasks/sec" if cleanup_time > 0 else "  Cleanup: Instant")

    return True


def test_priority_ordering():
    """Test that priority ordering works correctly."""
    print("\nTesting Priority Ordering")
    print("=" * 30)

    redis_mock = MockRedis()
    queue = TaskQueue()
    queue.client = redis_mock

    agent_name = "test_agent"

    # Create tasks with different priorities
    priorities = [5, 1, 3, 0, 2]  # Lower number = higher priority
    task_ids = []

    for i, priority in enumerate(priorities):
        task = Task(
            id=f"task_{i}",
            agent=agent_name,
            payload={"priority": priority},
            priority=priority,
        )
        queue.enqueue(task)
        task_ids.append(task.id)

    print(f"Enqueued tasks with priorities: {priorities}")

    # Dequeue tasks and check order
    dequeued_priorities = []
    while True:
        task = queue.dequeue(agent_name)
        if task is None:
            break
        dequeued_priorities.append(task.priority)

    expected_order = sorted(priorities)  # Should be [0, 1, 2, 3, 5]
    print(f"Dequeued in priority order: {dequeued_priorities}")
    print(f"Expected order: {expected_order}")

    if dequeued_priorities == expected_order:
        print("✓ Priority ordering works correctly")
        return True
    else:
        print("✗ Priority ordering failed")
        return False


if __name__ == "__main__":
    print("Legion TaskQueue Performance Test")
    print("=" * 40)
    
    success = True
    
    try:
        success &= test_priority_ordering()
        success &= test_queue_performance()
        
        if success:
            print("\n🎉 All performance tests passed!")
        else:
            print("\n❌ Some tests failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 