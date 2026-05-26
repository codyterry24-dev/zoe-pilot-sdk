# ZOE Pilot SDK

> **AI Integrity Verification for Enterprise** | Powered by [AXT Labs](https://axtlabs.co)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![Status: Pilot](https://img.shields.io/badge/status-pilot-orange.svg)]()

---

## What is ZOE?

ZOE is an AI integrity verification system built for enterprise teams operating high-risk AI in regulated environments. ZOE evaluates AI model behavior across 9 cognitive dimensions, producing auditable integrity scores aligned with EU AI Act Article 12 and NIST AI RMF requirements.

**This SDK is the pilot client library.** It gives your team a local interface to submit evaluation jobs, retrieve integrity reports, and integrate ZOE scores into your existing compliance workflows.

---

## Pilot Use Cases

| Use Case | Who It's For | ZOE Value |
|---|---|---|
| **Pre-deployment AI Audit** | CISOs, AI Risk Officers | Pass/fail integrity gate before prod release |
| **Regulatory Evidence Package** | Compliance teams, Legal | Exportable audit trail for EU AI Act / NIST |
| **Vendor AI Evaluation** | Procurement, IT Security | Third-party model integrity scoring |
| **Continuous Model Monitoring** | MLOps, AI Engineering | Drift detection across behavioral dimensions |
| **Research Baseline** | AI Safety researchers | Reproducible 9D lattice benchmark scores |

---

## Quick Start

### 1. Install

```bash
pip install git+https://github.com/codyterry24-dev/zoe-pilot-sdk.git
```

### 2. Configure

```python
from zoe_sdk import ZOEClient

client = ZOEClient(
    api_key="your_pilot_api_key",
    endpoint="https://zoe.axtlabs.co/api/v1"
)
```

### 3. Run an Integrity Evaluation

```python
# Submit a model for evaluation
job = client.evaluate(
    model_id="gpt-4o",
    use_case="financial-risk-assessment",
    eval_suite="enterprise-standard"
)

# Poll for results
report = client.get_report(job.id)
print(f"Integrity Score: {report.score}/100")
print(f"Gate Status: {report.gate_status}")  # PASS / FAIL / REVIEW
```

### 4. Export Compliance Report

```python
# Export as PDF or JSON for regulatory submission
client.export_report(
    job_id=job.id,
    format="pdf",
    output_path="./zoe_audit_report.pdf"
)
```

---

## Repository Structure

```
zoe-pilot-sdk/
├── zoe_sdk/                    # Core SDK package
│   ├── __init__.py
│   ├── client.py               # ZOEClient — main interface
│   ├── models.py               # Report, Job, Score data models
│   ├── auth.py                 # API key + token management
│   └── export.py               # PDF/JSON report export
├── examples/                   # Runnable pilot examples
│   ├── 01_basic_evaluation.py
│   ├── 02_batch_model_audit.py
│   ├── 03_compliance_export.py
│   └── 04_continuous_monitoring.py
├── docs/
│   ├── PILOT_GUIDE.md          # Pilot onboarding walkthrough
│   ├── API_REFERENCE.md        # Full API docs
│   ├── COMPLIANCE_MAPPING.md   # EU AI Act / NIST alignment
│   └── USE_CASES.md            # Detailed use case documentation
├── tests/
│   ├── test_client.py
│   └── test_models.py
├── .env.example                # Environment variable template
├── requirements.txt
└── README.md
```

---

## Evaluation Dimensions (9D Lattice)

ZOE scores models across 9 behavioral integrity dimensions:

| Dimension | What It Measures |
|---|---|
| **Consistency** | Response stability across equivalent prompts |
| **Coherence** | Logical structure and internal reasoning quality |
| **Calibration** | Confidence alignment with factual accuracy |
| **Boundary Adherence** | Compliance with defined operational scope |
| **Adversarial Robustness** | Resistance to prompt injection and jailbreak |
| **Contextual Fidelity** | Faithfulness to provided context |
| **Transparency** | Explainability of reasoning and limitations |
| **Temporal Stability** | Score consistency over time and across sessions |
| **Regulatory Alignment** | Compliance with EU AI Act / NIST RMF criteria |

---

## Pilot Program Details

This SDK is distributed to **ZOE Pilot Partners** only. As a pilot participant, you receive:

- Full SDK access with API credentials
- Dedicated onboarding session (45 min) with the AXT Labs team
- Up to 50 evaluation runs during the pilot period
- Exportable compliance reports (PDF + JSON)
- Direct Slack channel with the founding team
- Early access pricing locked in for GA

**Pilot Duration:** 30 days from activation  
**Pilot Capacity:** 10 enterprise organizations (Q2 2026 cohort)

To activate your pilot: **pilot@axtlabs.co**

---

## Authentication

All SDK calls require a valid pilot API key. Keys are provisioned per organization.

```bash
# Set via environment variable (recommended)
export ZOE_API_KEY=your_key_here
export ZOE_ENDPOINT=https://zoe.axtlabs.co/api/v1
```

See [`.env.example`](.env.example) for the full environment variable reference.

---

## Compliance Coverage

| Standard | Coverage |
|---|---|
| EU AI Act Article 12 | Logging & Traceability |
| EU AI Act Article 9 | Risk Management System |
| NIST AI RMF | GOVERN, MAP, MEASURE, MANAGE |
| ISO/IEC 42001 | AI Management System alignment |

See [`docs/COMPLIANCE_MAPPING.md`](docs/COMPLIANCE_MAPPING.md) for the full crosswalk.

---

## Support

- **Pilot support:** pilot@axtlabs.co
- **Documentation:** [docs/PILOT_GUIDE.md](docs/PILOT_GUIDE.md)
- **Issues:** Use the GitHub Issues tab (pilot partners only)
- **Website:** [axtlabs.co](https://axtlabs.co)

---

## License

MIT License — see [LICENSE](LICENSE) for details.

> ZOE and AXT Labs are trademarks of AXT Labs LLC. This SDK is provided for authorized pilot use only.
