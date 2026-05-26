# ZOE Pilot Program — Getting Started Guide

> Version 0.1.0-pilot | AXT Labs | support@axtlabs.co

## Overview

This guide walks your team through onboarding to the ZOE pilot program in under 30 minutes. By the end, you will have submitted your first AI evaluation job and received an IntegrityReport with 9-dimension scores.

---

## Prerequisites

| Requirement | Details |
|---|---|
| Python | 3.9 or higher |
| ZOE API Key | Provided by AXT Labs onboarding team |
| Access | `pip` + internet access to `api.axtlabs.co` |

---

## Step 1: Install the SDK

```bash
pip install git+https://github.com/codyterry24-dev/zoe-pilot-sdk.git
```

## Step 2: Configure Environment

Create a `.env` file in your project root:

```bash
ZOE_API_KEY=your-pilot-key-here
ZOE_ENDPOINT=https://api.axtlabs.co/zoe
ZOE_TIMEOUT=30
```

## Step 3: Run Your First Evaluation

```python
from zoe_sdk import ZOEClient

client = ZOEClient()  # reads ZOE_API_KEY from environment

job = client.evaluate(
    model_id="your-model-name",
    dataset_id="your-eval-dataset",
    dimensions=["consistency", "transparency", "robustness"]
)

print(f"Job submitted: {job.job_id} | Status: {job.status}")

# Poll until complete
report = client.get_report(job.job_id)
print(f"Overall Score: {report.overall_score:.3f}")
print(f"Pass/Fail: {'PASS' if report.passed else 'FAIL'}")
```

---

## The 9-Dimension Integrity Lattice

ZOE evaluates AI models across 9 cognitive dimensions aligned with EU AI Act Article 12 and NIST AI RMF:

| # | Dimension | Description |
|---|---|---|
| 1 | Consistency | Behavioral stability across equivalent inputs |
| 2 | Transparency | Reasoning traceability and explainability |
| 3 | Robustness | Performance under adversarial and edge conditions |
| 4 | Fairness | Demographic parity and disparate impact detection |
| 5 | Accuracy | Task performance against ground truth |
| 6 | Privacy | Data minimization and PII handling verification |
| 7 | Security | Resistance to prompt injection and jailbreaks |
| 8 | Reliability | Uptime, latency, and graceful degradation |
| 9 | Compliance | Regulatory alignment (EU AI Act, NIST, FERPA) |

Each dimension returns a `DimensionScore` with `score` (0.0–1.0), `passed` (bool), and `evidence` list.

---

## Interpreting Your Report

- **Overall Score ≥ 0.80**: Model passes ZOE integrity gate
- **Overall Score 0.60–0.79**: Conditional — remediation required before production
- **Overall Score < 0.60**: Fail — model does not meet high-risk AI deployment standards

The `IntegrityReport` is exportable as JSON for regulatory evidence packages.

```python
report_json = client.export_report(job.job_id, format="json")
```

---

## Support

- Email: support@axtlabs.co
- Pilot Slack: Provided in onboarding email
- Docs: https://github.com/codyterry24-dev/zoe-pilot-sdk/tree/main/docs
