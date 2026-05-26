"""
Unit tests for ZOEClient
Test suite: test_client
AXT Labs | zoe-pilot-sdk v0.1.0-pilot

All HTTP calls are intercepted with the `responses` library.
No real network calls are made during testing.
"""

import pytest
import responses as rsps_lib
from responses import RequestsMock
from unittest.mock import patch
import json

from zoe_sdk.client import ZOEClient
from zoe_sdk.models import EvaluationJob, IntegrityReport
from zoe_sdk.auth import AuthenticationError


BASE_URL = "https://zoe.axtlabs.co/api/v1"
TEST_API_KEY = "zoe_test_key_abc123"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    return ZOEClient(api_key=TEST_API_KEY, endpoint=BASE_URL)


@pytest.fixture
def mock_job_response():
    return {
        "id": "job_mock_001",
        "status": "pending",
        "model_id": "gpt-4o",
        "use_case": "financial-risk-assessment",
        "eval_suite": "enterprise-standard",
        "created_at": "2026-05-26T18:00:00Z",
        "metadata": {},
    }


@pytest.fixture
def mock_complete_job_response():
    return {
        "id": "job_mock_001",
        "status": "complete",
        "model_id": "gpt-4o",
        "use_case": "financial-risk-assessment",
        "eval_suite": "enterprise-standard",
        "created_at": "2026-05-26T18:00:00Z",
        "metadata": {},
    }


@pytest.fixture
def mock_report_response():
    return {
        "job_id": "job_mock_001",
        "model_id": "gpt-4o",
        "use_case": "financial-risk-assessment",
        "score": 82.3,
        "gate_status": "PASS",
        "eval_suite": "enterprise-standard",
        "generated_at": "2026-05-26T18:02:00Z",
        "dimensions": [
            {"dimension": "Consistency", "score": 88.5, "confidence": 0.92, "status": "pass"},
            {"dimension": "Coherence", "score": 91.0, "confidence": 0.95, "status": "pass"},
            {"dimension": "Calibration", "score": 74.2, "confidence": 0.78, "status": "review"},
            {"dimension": "Boundary Adherence", "score": 79.1, "confidence": 0.88, "status": "pass"},
            {"dimension": "Adversarial Robustness", "score": 82.1, "confidence": 0.90, "status": "pass"},
            {"dimension": "Contextual Fidelity", "score": 93.7, "confidence": 0.96, "status": "pass"},
            {"dimension": "Transparency", "score": 79.4, "confidence": 0.85, "status": "pass"},
            {"dimension": "Temporal Stability", "score": 86.0, "confidence": 0.89, "status": "pass"},
            {"dimension": "Regulatory Alignment", "score": 68.9, "confidence": 0.81, "status": "review"},
        ],
        "regulatory_flags": [],
        "recommendations": [],
        "metadata": {},
    }


# ---------------------------------------------------------------------------
# Authentication tests
# ---------------------------------------------------------------------------

class TestAuthentication:
    def test_raises_if_no_api_key(self):
        with patch.dict("os.environ", {}, clear=True):
            # Remove ZOE_API_KEY from env if set
            import os
            os.environ.pop("ZOE_API_KEY", None)
            with pytest.raises(AuthenticationError):
                ZOEClient()

    def test_accepts_api_key_argument(self):
        c = ZOEClient(api_key="zoe_explicit_key")
        assert c.api_key == "zoe_explicit_key"

    def test_accepts_api_key_from_env(self):
        with patch.dict("os.environ", {"ZOE_API_KEY": "zoe_env_key"}):
            c = ZOEClient()
            assert c.api_key == "zoe_env_key"

    def test_bearer_token_set_in_headers(self, client):
        assert client._session.headers["Authorization"] == f"Bearer {TEST_API_KEY}"

    def test_sdk_version_header_set(self, client):
        assert "X-ZOE-SDK-Version" in client._session.headers
        assert "pilot" in client._session.headers["X-ZOE-SDK-Version"]

    def test_warns_on_invalid_key_format(self):
        with pytest.warns(UserWarning, match="does not match expected format"):
            ZOEClient(api_key="invalid_key_format")


# ---------------------------------------------------------------------------
# ZOEClient initialization tests
# ---------------------------------------------------------------------------

class TestClientInit:
        def test_default_endpoint(self, monkeypatch):
                monkeypatch.delenv("ZOE_ENDPOINT", raising=False)
c = ZOEClient(api_key=TEST_API_KEY)
        assert c.endpoint == "https://zoe.axtlabs.co/api/v1"

    def test_custom_endpoint(self):
        c = ZOEClient(api_key=TEST_API_KEY, endpoint="https://staging.zoe.axtlabs.co/api/v1")
        assert c.endpoint == "https://staging.zoe.axtlabs.co/api/v1"

    def test_endpoint_trailing_slash_stripped(self):
        c = ZOEClient(api_key=TEST_API_KEY, endpoint="https://zoe.axtlabs.co/api/v1/")
        assert not c.endpoint.endswith("/")

    def test_default_timeout(self):
        c = ZOEClient(api_key=TEST_API_KEY)
        assert c.timeout == 30

    def test_custom_timeout(self):
        c = ZOEClient(api_key=TEST_API_KEY, timeout=60)
        assert c.timeout == 60


# ---------------------------------------------------------------------------
# evaluate() tests
# ---------------------------------------------------------------------------

class TestEvaluate:
    @rsps_lib.activate
    def test_evaluate_returns_evaluation_job(self, client, mock_job_response):
        rsps_lib.add(
            rsps_lib.POST,
            f"{BASE_URL}/evaluations",
            json=mock_job_response,
            status=200,
        )
        job = client.evaluate(
            model_id="gpt-4o",
            use_case="financial-risk-assessment",
        )
        assert isinstance(job, EvaluationJob)
        assert job.id == "job_mock_001"
        assert job.status == "pending"
        assert job.model_id == "gpt-4o"

    @rsps_lib.activate
    def test_evaluate_sends_correct_payload(self, client, mock_job_response):
        rsps_lib.add(
            rsps_lib.POST,
            f"{BASE_URL}/evaluations",
            json=mock_job_response,
            status=200,
        )
        client.evaluate(
            model_id="claude-3-5-sonnet",
            use_case="hr-screening",
            eval_suite="enterprise-standard",
        )
        sent_body = json.loads(rsps_lib.calls[0].request.body)
        assert sent_body["model_id"] == "claude-3-5-sonnet"
        assert sent_body["use_case"] == "hr-screening"
        assert sent_body["eval_suite"] == "enterprise-standard"

    @rsps_lib.activate
    def test_evaluate_raises_on_http_error(self, client):
        rsps_lib.add(
            rsps_lib.POST,
            f"{BASE_URL}/evaluations",
            json={"error": "Unauthorized"},
            status=401,
        )
        import requests
        with pytest.raises(requests.exceptions.HTTPError):
            client.evaluate(model_id="gpt-4o", use_case="test")


# ---------------------------------------------------------------------------
# get_report() tests
# ---------------------------------------------------------------------------

class TestGetReport:
    @rsps_lib.activate
    def test_get_report_no_wait_returns_integrity_report(
        self, client, mock_report_response
    ):
        rsps_lib.add(
            rsps_lib.GET,
            f"{BASE_URL}/evaluations/job_mock_001/report",
            json=mock_report_response,
            status=200,
        )
        report = client.get_report("job_mock_001", wait=False)
        assert isinstance(report, IntegrityReport)
        assert report.job_id == "job_mock_001"
        assert report.score == 82.3
        assert report.gate_status == "PASS"

    @rsps_lib.activate
    def test_get_report_deserializes_nine_dimensions(
        self, client, mock_report_response
    ):
        rsps_lib.add(
            rsps_lib.GET,
            f"{BASE_URL}/evaluations/job_mock_001/report",
            json=mock_report_response,
            status=200,
        )
        report = client.get_report("job_mock_001", wait=False)
        assert len(report.dimensions) == 9

    @rsps_lib.activate
    def test_get_report_raises_on_404(self, client):
        rsps_lib.add(
            rsps_lib.GET,
            f"{BASE_URL}/evaluations/nonexistent/report",
            json={"error": "Not found"},
            status=404,
        )
        import requests
        with pytest.raises(requests.exceptions.HTTPError):
            client.get_report("nonexistent", wait=False)


# ---------------------------------------------------------------------------
# list_jobs() tests
# ---------------------------------------------------------------------------

class TestListJobs:
    @rsps_lib.activate
    def test_list_jobs_returns_list_of_evaluation_jobs(self, client, mock_job_response):
        rsps_lib.add(
            rsps_lib.GET,
            f"{BASE_URL}/evaluations",
            json={"jobs": [mock_job_response, {**mock_job_response, "id": "job_002"}]},
            status=200,
        )
        jobs = client.list_jobs()
        assert isinstance(jobs, list)
        assert len(jobs) == 2
        assert all(isinstance(j, EvaluationJob) for j in jobs)

    @rsps_lib.activate
    def test_list_jobs_empty_response(self, client):
        rsps_lib.add(
            rsps_lib.GET,
            f"{BASE_URL}/evaluations",
            json={"jobs": []},
            status=200,
        )
        jobs = client.list_jobs()
        assert jobs == []

    @rsps_lib.activate
    def test_list_jobs_sends_limit_param(self, client, mock_job_response):
        rsps_lib.add(
            rsps_lib.GET,
            f"{BASE_URL}/evaluations",
            json={"jobs": [mock_job_response]},
            status=200,
        )
        client.list_jobs(limit=5)
        assert "limit=5" in rsps_lib.calls[0].request.url


# ---------------------------------------------------------------------------
# export_report() tests
# ---------------------------------------------------------------------------

class TestExportReport:
    def test_raises_on_invalid_format(self, client):
        with pytest.raises(ValueError, match="Unsupported format"):
            client.export_report("job_001", format="xlsx")

    @rsps_lib.activate
    def test_export_pdf_calls_correct_endpoint(self, client, tmp_path):
        rsps_lib.add(
            rsps_lib.GET,
            f"{BASE_URL}/evaluations/job_mock_001/export",
            body=b"%PDF-1.4 fake content",
            status=200,
            content_type="application/pdf",
        )
        output = tmp_path / "report"
        path = client.export_report("job_mock_001", format="pdf", output_path=str(output))
        assert path.endswith(".pdf")
        assert "format=pdf" in rsps_lib.calls[0].request.url
