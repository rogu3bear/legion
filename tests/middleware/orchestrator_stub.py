import types

orchestrator_stub = types.ModuleType("legion.orchestrator")


class Orchestrator:
    def run_once(self):
        return []


orchestrator_stub.Orchestrator = Orchestrator
