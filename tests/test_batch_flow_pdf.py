import asyncio
import json
from fastapi.testclient import TestClient
from backend.main import app


client = TestClient(app)


def test_batch_flow_pdf_end_to_end():
    # Start batch
    req = {
        "resume_text": "John Doe\njohn@example.com\nSUMMARY\nGreat engineer\nEXPERIENCE\nAcme Corp\n- Did things",
        "job_urls": ["https://example.com/job/1"],
        "output_format": "pdf",
        "template": "modern"
    }
    start = client.post("/api/enhanced-batch/process", json=req)
    assert start.status_code == 200
    batch_id = start.json()["batch_job_id"]

    # Poll status until completed
    for _ in range(30):
        status = client.get(f"/api/enhanced-batch/status/{batch_id}")
        assert status.status_code == 200
        state = status.json()["status"]["state"]
        if state == "completed":
            break
        import time
        time.sleep(0.5)
    assert state == "completed"

    # Get results
    results_resp = client.get(f"/api/enhanced-batch/results/{batch_id}")
    assert results_resp.status_code == 200
    results = results_resp.json()["results"]
    assert len(results) >= 1
    first = results[0]
    frd = first.get("formatted_resume_data")
    assert frd is None or (frd.get("format") == "pdf" and frd.get("download_url"))

    # If we have a pdf, download it
    if frd and frd.get("download_url"):
        download_url = frd["download_url"]
        dl_resp = client.get(download_url)
        assert dl_resp.status_code == 200
        assert dl_resp.headers.get("content-type") == "application/pdf"
        assert dl_resp.content[:4] == b"%PDF"


