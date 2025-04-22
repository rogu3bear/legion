"""Legion Python agents package init."""

from .architect import ArchitectAgent  # noqa: F401
from .developer import DeveloperAgent  # noqa: F401
from .doctor import DoctorAgent  # noqa: F401
from .echo import EchoAgent  # noqa: F401
from .healthcheck import HealthcheckAgent  # noqa: F401
from .metrics import MetricsAgent  # noqa: F401
from .ping import PingAgent  # noqa: F401
from .researcher import ResearcherAgent  # noqa: F401
from .therapist import TherapistAgent  # noqa: F401
from .ux_designer import UxDesignerAgent  # noqa: F401

# This __init__ intentionally imports all agents
# for easier registration and potential future dynamic loading.
# The noqa F401 suppresses unused import warnings here.

__all__ = [
    'ArchitectAgent',
    'MetricsAgent', 
    'UxDesignerAgent',
    'TherapistAgent',
    'PingAgent',
    'EchoAgent',
    'HealthcheckAgent',
    'DoctorAgent',
    'ResearcherAgent'
]
