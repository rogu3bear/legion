"""Legion Python agents package init."""

from .architect import ArchitectAgent
from .echo import EchoAgent
from .metrics import MetricsAgent
from .ping import PingAgent
from .therapist import TherapistAgent
from .ux_designer import UxDesignerAgent
from .doctor import DoctorAgent
from .researcher import ResearcherAgent

# This __init__ intentionally imports all agents
# for easier registration and potential future dynamic loading.
# The noqa F401 suppresses unused import warnings here.

__all__ = [
    "ArchitectAgent",
    "EchoAgent",
    "MetricsAgent",
    "PingAgent",
    "TherapistAgent",
    "UxDesignerAgent",
    "DoctorAgent",
    "ResearcherAgent",
]
