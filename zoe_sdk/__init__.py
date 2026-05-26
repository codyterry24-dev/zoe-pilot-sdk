"""
ZOE Pilot SDK
AI integrity verification for enterprise
AXT Labs | https://axtlabs.co
"""

__version__ = "0.1.0-pilot"
__author__ = "AXT Labs"
__email__ = "pilot@axtlabs.co"

from .client import ZOEClient
from .models import EvaluationJob, IntegrityReport, DimensionScore

__all__ = [
    "ZOEClient",
    "EvaluationJob",
    "IntegrityReport",
    "DimensionScore",
]
