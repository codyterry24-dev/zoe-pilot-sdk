"""
Data models for ZOE Pilot SDK
AXT Labs | https://axtlabs.co
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class EvaluationJob:
    """Represents a submitted evaluation job."""
    id: str
    status: str  # pending | running | complete | failed
    model_id: str
    use_case: str
    eval_suite: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self):
        return f"<EvaluationJob id={self.id} status={self.status} model={self.model_id}>"


@dataclass
class DimensionScore:
    """Score for a single ZOE integrity dimension."""
    dimension: str
    score: float  # 0.0 - 100.0
    confidence: float  # 0.0 - 1.0
    status: str  # pass | fail | review
    evidence: Optional[str] = None

    def __repr__(self):
        return f"<DimensionScore {self.dimension}={self.score:.1f} [{self.status}]>"


@dataclass
class IntegrityReport:
    """Complete ZOE integrity evaluation report."""
    job_id: str
    model_id: str
    use_case: str
    score: float  # Composite 0-100 integrity score
    gate_status: str  # PASS | FAIL | REVIEW
    dimensions: list = field(default_factory=list)  # List[DimensionScore]
    generated_at: Optional[str] = None
    eval_suite: Optional[str] = None
    regulatory_flags: list = field(default_factory=list)
    recommendations: list = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        # Deserialize nested dimension scores if passed as dicts
        if self.dimensions and isinstance(self.dimensions[0], dict):
            self.dimensions = [DimensionScore(**d) for d in self.dimensions]

    def passed(self) -> bool:
        """Returns True if gate status is PASS."""
        return self.gate_status == "PASS"

    def failed_dimensions(self) -> list:
        """Returns dimensions that failed the integrity gate."""
        return [d for d in self.dimensions if d.status == "fail"]

    def summary(self) -> str:
        """Returns a human-readable one-line summary."""
        failed = len(self.failed_dimensions())
        return (
            f"ZOE Report [{self.gate_status}] "
            f"Score: {self.score:.1f}/100 | "
            f"Model: {self.model_id} | "
            f"Failures: {failed}/{len(self.dimensions)}"
        )

    def __repr__(self):
        return f"<IntegrityReport job={self.job_id} score={self.score:.1f} gate={self.gate_status}>"
