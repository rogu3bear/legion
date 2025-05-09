"""Legion Python agents package init."""

from .architect import ArchitectAgent
from .echo import EchoAgent
from .healthcheck import HealthcheckAgent
from .metrics import MetricsAgent
from .ping import PingAgent
from .therapist import TherapistAgent
from .ux_designer import UxDesignerAgent

# This __init__ intentionally imports all agents
# for easier registration and potential future dynamic loading.
# The noqa F401 suppresses unused import warnings here.

__all__ = [
    "ArchitectAgent",
    "EchoAgent",
    "HealthcheckAgent",
    "MetricsAgent",
    "PingAgent",
    "TherapistAgent",
    "UxDesignerAgent",
]
