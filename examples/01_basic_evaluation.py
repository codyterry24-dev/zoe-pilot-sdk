"""
Example 01: Basic Integrity Evaluation
=======================================
This example shows the minimal end-to-end flow for submitting a model
for ZOE integrity evaluation and retrieving the report.

Prerequisites:
    1. Set ZOE_API_KEY in your environment (see .env.example)
    2. Install dependencies: pip install -r requirements.txt

Run:
    python examples/01_basic_evaluation.py

AXT Labs | https://axtlabs.co | pilot@axtlabs.co
"""

import os
from dotenv import load_dotenv
from zoe_sdk import ZOEClient

# Load environment variables from .env if present
load_dotenv()


def main():
    # ------------------------------------------------------------------
    # 1. Initialize the ZOE client
    # ------------------------------------------------------------------
    client = ZOEClient(
        api_key=os.getenv("ZOE_API_KEY"),
        endpoint=os.getenv("ZOE_ENDPOINT"),  # Uses default if not set
    )
    print("ZOE Client initialized.")
    print(f"  Endpoint : {client.endpoint}")
    print(f"  SDK      : {client._session.headers.get('X-ZOE-SDK-Version')}")
    print()

    # ------------------------------------------------------------------
    # 2. Submit a model for evaluation
    # ------------------------------------------------------------------
    print("Submitting GPT-4o for financial risk evaluation...")
    job = client.evaluate(
        model_id="gpt-4o",
        use_case="financial-risk-assessment",
        eval_suite="enterprise-standard",
        metadata={
            "org": "Acme Financial Corp",
            "environment": "pre-production",
            "requestor": "compliance-team",
        },
    )
    print(f"  Job ID   : {job.id}")
    print(f"  Status   : {job.status}")
    print()

    # ------------------------------------------------------------------
    # 3. Wait for completion and retrieve report
    # ------------------------------------------------------------------
    print("Waiting for evaluation to complete (polling every 5s)...")
    report = client.get_report(job.id, wait=True)
    print()

    # ------------------------------------------------------------------
    # 4. Display results
    # ------------------------------------------------------------------
    print("=" * 60)
    print("ZOE INTEGRITY REPORT")
    print("=" * 60)
    print(f"  {report.summary()}")
    print()
    print("Dimension Breakdown:")
    for dim in report.dimensions:
        status_icon = "v" if dim.status == "pass" else ("!" if dim.status == "review" else "X")
        print(f"  [{status_icon}] {dim.dimension:<25} {dim.score:>5.1f}/100  (confidence: {dim.confidence:.0%})")
    print()

    if report.regulatory_flags:
        print("Regulatory Flags:")
        for flag in report.regulatory_flags:
            print(f"  - {flag}")
        print()

    if report.recommendations:
        print("Recommendations:")
        for rec in report.recommendations:
            print(f"  -> {rec}")
        print()

    # ------------------------------------------------------------------
    # 5. Export compliance report
    # ------------------------------------------------------------------
    output_path = f"./zoe_report_{job.id}"
    print(f"Exporting PDF compliance report to {output_path}.pdf ...")
    pdf_path = client.export_report(job.id, format="pdf", output_path=output_path)
    print(f"  Saved: {pdf_path}")
    print()

    print("Done. Gate status:", report.gate_status)
    if report.passed():
        print("Model PASSED integrity gate. Safe to proceed to production review.")
    else:
        print("Model FAILED or requires REVIEW. Do not deploy without remediation.")


if __name__ == "__main__":
    main()
