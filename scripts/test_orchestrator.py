import os
from src.orchestrator import Orchestrator
from src.legion_memory import LegionAgentMemory

def test_orchestrator_init():
    orch = Orchestrator()
    assert len(orch.agent_registry) > 0, "No agents loaded"
    for name in orch.agent_registry:
        mem_path = os.path.join("memory", name)
        assert os.path.isdir(mem_path), f"Memory dir missing for {name}"
        mem = LegionAgentMemory(name)
        assert isinstance(mem.get_task_log(), list), "Task log not list"
    print("Orchestrator and agent memory initialized successfully.")

if __name__ == "__main__":
    test_orchestrator_init() 