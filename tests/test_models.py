"""
Unit tests for ZOE SDK data models
Test suite: test_models
AXT Labs | zoe-pilot-sdk v0.1.0-pilot
"""

import pytest
from zoe_sdk.models import EvaluationJob, IntegrityReport, DimensionScore


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_dimension_scores():
    return [
        {"dimension": "Consistency", "score": 88.5, "confidence": 0.92, "status": "pass", "evidence": "Stable across 50 prompt variants"},
        {"dimension": "Coherence", "score": 91.0, "confidence": 0.95, "status": "pass", "evidence": None},
        {"dimension": "Calibration", "score": 74.2, "confidence": 0.78, "status": "review", "evidence": "Overconfident on ambiguous queries"},
        {"dimension": "Boundary Adherence", "score": 55.3, "confidence": 0.88, "status": "fail", "evidence": "Scope violations in 3 test cases"},
        {"dimension": "Adversarial Robustness", "score": 82.1, "confidence": 0.90, "status": "pass", "evidence": None},
        {"dimension": "Contextual Fidelity", "score": 93.7, "confidence": 0.96, "status": "pass", "evidence": None},
        {"dimension": "Transparency", "score": 79.4, "confidence": 0.85, "status": "pass", "evidence": None},
        {"dimension": "Temporal Stability", "score": 86.0, "confidence": 0.89, "status": "pass", "evidence": None},
        {"dimension": "Regulatory Alignment", "score": 68.9, "confidence": 0.81, "status": "review", "evidence": "NIST RMF MEASURE gap detected"},
    ]


@pytest.fixture
def passing_report(sample_dimension_scores):
    return IntegrityReport(
        job_id="job_test_001",
        model_id="gpt-4o",
        use_case="financial-risk-assessment",
        score=82.3,
        gate_status="PASS",
        dimensions=sample_dimension_scores,
        generated_at="2026-05-26T18:00:00Z",
        eval_suite="enterprise-standard",
    )


@pytest.fixture
def failing_report(sample_dimension_scores):
    return IntegrityReport(
        job_id="job_test_002",
        model_id="open-source-model-v2",
        use_case="medical-triage",
        score=41.7,
        gate_status="FAIL",
        dimensions=sample_dimension_scores,
        generated_at="2026-05-26T18:05:00Z",
        eval_suite="enterprise-standard",
        regulatory_flags=["EU_AI_ACT_ART12", "NIST_MEASURE"],
        recommendations=["Retrain on boundary adherence corpus", "Add NIST RMF MEASURE controls"],
    )


# ---------------------------------------------------------------------------
# DimensionScore tests
# ---------------------------------------------------------------------------

class TestDimensionScore:
    def test_creation_with_all_fields(self):
        ds = DimensionScore(
            dimension="Consistency",
            score=88.5,
            confidence=0.92,
            status="pass",
            evidence="Stable output",
        )
        assert ds.dimension == "Consistency"
        assert ds.score == 88.5
        assert ds.confidence == 0.92
        assert ds.status == "pass"
        assert ds.evidence == "Stable output"

    def test_creation_without_evidence(self):
        ds = DimensionScore(
            dimension="Coherence",
            score=91.0,
            confidence=0.95,
            status="pass",
        )
        assert ds.evidence is None

    def test_repr_format(self):
        ds = DimensionScore(dimension="Consistency", score=88.5, confidence=0.92, status="pass")
        r = repr(ds)
        assert "Consistency" in r
        assert "88.5" in r
        assert "pass" in r

    def test_score_boundary_values(self):
        ds_min = DimensionScore(dimension="X", score=0.0, confidence=0.0, status="fail")
        ds_max = DimensionScore(dimension="X", score=100.0, confidence=1.0, status="pass")
        assert ds_min.score == 0.0
        assert ds_max.score == 100.0


# ---------------------------------------------------------------------------
# EvaluationJob tests
# ---------------------------------------------------------------------------

class TestEvaluationJob:
    def test_creation_minimal(self):
        job = EvaluationJob(
            id="job_abc123",
            status="pending",
            model_id="gpt-4o",
            use_case="financial-risk",
            eval_suite="enterprise-standard",
        )
        assert job.id == "job_abc123"
        assert job.status == "pending"
        assert job.model_id == "gpt-4o"
        assert job.metadata == {}

    def test_creation_with_metadata(self):
        job = EvaluationJob(
            id="job_xyz",
            status="running",
            model_id="claude-3-5-sonnet",
            use_case="hr-screening",
            eval_suite="enterprise-standard",
            metadata={"org": "Acme Corp", "env": "staging"},
        )
        assert job.metadata["org"] == "Acme Corp"

    def test_repr_contains_key_fields(self):
        job = EvaluationJob(
            id="job_001",
            status="complete",
            model_id="gpt-4o",
            use_case="test",
            eval_suite="enterprise-standard",
        )
        r = repr(job)
        assert "job_001" in r
        assert "complete" in r
        assert "gpt-4o" in r

    def test_all_status_values(self):
        for status in ["pending", "running", "complete", "failed"]:
            job = EvaluationJob(
                id="job_s",
                status=status,
                model_id="m",
                use_case="u",
                eval_suite="e",
            )
            assert job.status == status


# ---------------------------------------------------------------------------
# IntegrityReport tests
# ---------------------------------------------------------------------------

class TestIntegrityReport:
    def test_passed_returns_true_for_pass_status(self, passing_report):
        assert passing_report.passed() is True

    def test_passed_returns_false_for_fail_status(self, failing_report):
        assert failing_report.passed() is False

    def test_failed_dimensions_returns_only_failures(self, passing_report):
        failures = passing_report.failed_dimensions()
        assert all(d.status == "fail" for d in failures)
        assert len(failures) == 1
        assert failures[0].dimension == "Boundary Adherence"

    def test_failed_dimensions_empty_when_all_pass(self):
        report = IntegrityReport(
            job_id="j",
            model_id="m",
            use_case="u",
            score=95.0,
            gate_status="PASS",
            dimensions=[
                DimensionScore("Consistency", 95.0, 0.99, "pass"),
            ],
        )
        assert report.failed_dimensions() == []

    def test_summary_format(self, passing_report):
        s = passing_report.summary()
        assert "PASS" in s
        assert "82.3" in s
        assert "gpt-4o" in s

    def test_dimensions_deserialized_from_dicts(self, sample_dimension_scores):
        report = IntegrityReport(
            job_id="j",
            model_id="m",
            use_case="u",
            score=75.0,
            gate_status="REVIEW",
            dimensions=sample_dimension_scores,  # list of dicts
        )
        assert all(isinstance(d, DimensionScore) for d in report.dimensions)

    def test_repr_contains_key_fields(self, passing_report):
        r = repr(passing_report)
        assert "job_test_001" in r
        assert "82.3" in r
        assert "PASS" in r

    def test_regulatory_flags_default_empty(self, passing_report):
        assert passing_report.regulatory_flags == []

    def test_recommendations_populated(self, failing_report):
        assert len(failing_report.recommendations) == 2
        assert "boundary adherence" in failing_report.recommendations[0].lower()

    def test_score_range_valid(self, passing_report):
        assert 0.0 <= passing_report.score <= 100.0

    def test_nine_dimensions_present(self, passing_report):
        assert len(passing_report.dimensions) == 9
