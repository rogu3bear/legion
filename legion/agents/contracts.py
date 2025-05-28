from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class IArchitectAgent(ABC):
    """
    Contract for ArchitectAgent:
    - handle_review() -> None
    - list_repo() -> List[str]
    - set_log_paths(log_path: Optional[str], report_path: Optional[str]) -> None
    - read_logs() -> List[Dict[str, Any]]
    - extract_llm_metrics() -> Dict[str, Any]
    - compose_summary() -> str

    Config:
    - system_prompt: str

    Errors:
    - File I/O errors in read_logs/extract_llm_metrics
    """

    @abstractmethod
    async def handle_review(self) -> None:
        pass

    @abstractmethod
    def list_repo(self) -> List[str]:
        pass

    @abstractmethod
    def set_log_paths(
        self, log_path: Optional[str] = None, report_path: Optional[str] = None
    ) -> None:
        pass

    @abstractmethod
    def read_logs(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def extract_llm_metrics(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def compose_summary(self) -> str:
        pass


class IMetricsAgent(ABC):
    """
    Contract for MetricsAgent:
    - report() -> None
    - handle_report() -> Any
    - get_agent_channels() -> List[Any]
    - set_log_paths(log_path: Optional[str]) -> None
    - read_logs() -> List[Dict[str, Any]]
    - compose_summary() -> str

    Config:
    - system_prompt: str

    Errors:
    - Channel access errors
    - JSON parsing errors in read_logs
    """

    @abstractmethod
    async def report(self) -> None:
        pass

    @abstractmethod
    async def handle_report(self) -> Any:
        pass

    @abstractmethod
    def get_agent_channels(self) -> List[Any]:
        pass

    @abstractmethod
    def set_log_paths(self, log_path: Optional[str] = None) -> None:
        pass

    @abstractmethod
    def read_logs(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def compose_summary(self) -> str:
        pass


class ITherapistAgent(ABC):
    """
    Contract for TherapistAgent:
    - set_log_paths(log_path: Optional[str]) -> None
    - read_logs() -> List[Dict[str, Any]]
    - compose_summary() -> str
    - handle_self_assessment() -> Any

    Config:
    - system_prompt: str

    Errors:
    - JSON parsing errors in read_logs
    """

    @abstractmethod
    def set_log_paths(self, log_path: Optional[str] = None) -> None:
        pass

    @abstractmethod
    def read_logs(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def compose_summary(self) -> str:
        pass

    @abstractmethod
    async def handle_self_assessment(self) -> Any:
        pass




class IEchoAgent(ABC):
    """
    Contract for EchoAgent:
    - handle_echo(message: str) -> Any

    Config:
    - system_prompt: str

    Errors:
    - None
    """

    @abstractmethod
    async def handle_echo(self, message: str) -> Any:
        pass


# Mapping for validation
AGENT_CONTRACTS = {
    "architect_agent": IArchitectAgent
    "metrics_agent": IMetricsAgent
    "therapist_agent": ITherapistAgent
    "echo_agent": IEchoAgent
}


def validate_all_agents(instances: Dict[str, Any]) -> None:
    """
    Validate that each agent instance implements its contract methods.
    """
    for name, agent in instances.items():
        contract = AGENT_CONTRACTS.get(name)
        if not contract:
            continue
        missing = []
        for method in contract.__abstractmethods__:
            if not hasattr(agent, method):
                missing.append(method)
        if missing:
            raise TypeError(f"Agent '{name}' missing required methods: {missing}")
