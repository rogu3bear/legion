"""Legion Python agents package init."""

from .architect import ArchitectAgent
from .doctor import DoctorAgent
from .echo import EchoAgent
from .healthcheck import HealthcheckAgent
from .metrics import MetricsAgent
from .ping import PingAgent
from .researcher import ResearcherAgent
from .therapist import TherapistAgent
from .ux_designer import UxDesignerAgent

# This __init__ intentionally imports all agents
# for easier registration and potential future dynamic loading.
# The noqa F401 suppresses unused import warnings here.

__all__ = [
    "ArchitectAgent",
    "DoctorAgent",
    "EchoAgent",
    "HealthcheckAgent",
    "MetricsAgent",
    "PingAgent",
    "ResearcherAgent",
    "TherapistAgent",
    "UxDesignerAgent",
]
