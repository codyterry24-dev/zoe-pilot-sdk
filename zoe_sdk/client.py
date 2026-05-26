"""
ZOEClient — Main interface for the ZOE Pilot SDK
AXT Labs | https://axtlabs.co
"""

import os
import time
from typing import Optional

import requests

from .models import EvaluationJob, IntegrityReport
from .auth import resolve_api_key


class ZOEClient:
    """
    Primary client for the ZOE integrity verification API.

    Usage:
        client = ZOEClient(api_key="your_key")
        job = client.evaluate(model_id="gpt-4o", use_case="financial-risk")
        report = client.get_report(job.id)
    """

    DEFAULT_ENDPOINT = "https://zoe.axtlabs.co/api/v1"
    POLL_INTERVAL_SECONDS = 5
    MAX_POLL_ATTEMPTS = 60

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        timeout: int = 30,
    ):
        self.api_key = resolve_api_key(api_key)
        self.endpoint = (endpoint or os.getenv("ZOE_ENDPOINT") or self.DEFAULT_ENDPOINT).rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-ZOE-SDK-Version": "0.1.0-pilot",
        })

    def evaluate(
        self,
        model_id: str,
        use_case: str,
        eval_suite: str = "enterprise-standard",
        metadata: Optional[dict] = None,
    ) -> EvaluationJob:
        """
        Submit a model for integrity evaluation.

        Args:
            model_id: Identifier for the model (e.g. "gpt-4o", "claude-3-5-sonnet")
            use_case: Business use case context (e.g. "financial-risk-assessment")
            eval_suite: Evaluation suite to run (default: "enterprise-standard")
            metadata: Optional dict of additional metadata to attach to the job

        Returns:
            EvaluationJob with job ID and initial status
        """
        payload = {
            "model_id": model_id,
            "use_case": use_case,
            "eval_suite": eval_suite,
            "metadata": metadata or {},
        }
        response = self._session.post(
            f"{self.endpoint}/evaluations",
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return EvaluationJob(**response.json())

    def get_report(
        self,
        job_id: str,
        wait: bool = True,
    ) -> IntegrityReport:
        """
        Retrieve the integrity report for a completed evaluation job.

        Args:
            job_id: The job ID returned by evaluate()
            wait: If True, polls until the job completes (default: True)

        Returns:
            IntegrityReport with score, gate status, and dimension breakdown
        """
        if wait:
            return self._poll_for_report(job_id)

        response = self._session.get(
            f"{self.endpoint}/evaluations/{job_id}/report",
            timeout=self.timeout,
        )
        response.raise_for_status()
        return IntegrityReport(**response.json())

    def export_report(
        self,
        job_id: str,
        format: str = "pdf",
        output_path: str = "./zoe_report",
    ) -> str:
        """
        Export a compliance report in PDF or JSON format.

        Args:
            job_id: The job ID to export
            format: Export format — "pdf" or "json" (default: "pdf")
            output_path: File path for the exported report (without extension)

        Returns:
            Absolute path to the exported file
        """
        if format not in ("pdf", "json"):
            raise ValueError(f"Unsupported format: {format}. Use 'pdf' or 'json'.")

        response = self._session.get(
            f"{self.endpoint}/evaluations/{job_id}/export",
            params={"format": format},
            timeout=self.timeout,
            stream=True,
        )
        response.raise_for_status()

        ext = ".pdf" if format == "pdf" else ".json"
        full_path = output_path if output_path.endswith(ext) else output_path + ext

        with open(full_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return os.path.abspath(full_path)

    def list_jobs(
        self,
        limit: int = 20,
        status: Optional[str] = None,
    ) -> list:
        """
        List evaluation jobs for your organization.

        Args:
            limit: Max number of jobs to return (default: 20)
            status: Filter by status — "pending", "running", "complete", "failed"

        Returns:
            List of EvaluationJob objects
        """
        params = {"limit": limit}
        if status:
            params["status"] = status

        response = self._session.get(
            f"{self.endpoint}/evaluations",
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return [EvaluationJob(**job) for job in response.json().get("jobs", [])]

    def _poll_for_report(self, job_id: str) -> IntegrityReport:
        """Poll until evaluation completes and return the report."""
        for attempt in range(self.MAX_POLL_ATTEMPTS):
            response = self._session.get(
                f"{self.endpoint}/evaluations/{job_id}",
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            status = data.get("status")

            if status == "complete":
                return self.get_report(job_id, wait=False)
            elif status == "failed":
                raise RuntimeError(f"Evaluation job {job_id} failed: {data.get('error')}")

            time.sleep(self.POLL_INTERVAL_SECONDS)

        raise TimeoutError(f"Job {job_id} did not complete within the polling window.")
