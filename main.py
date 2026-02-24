from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import os
import sys
import io

# Force UTF-8 encoding for standard output and error to prevent UnicodeEncodeError with emojis in Windows console
if sys.stdout and getattr(sys.stdout, 'buffer', None):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr and getattr(sys.stderr, 'buffer', None):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import uuid
import agentops
from database import create_analysis_record, get_analysis, get_all_analyses
from celery_worker import analyze_document_task

# Initialize AgentOps tracing
agentops.init()

app = FastAPI(title="Financial Document Analyzer")


# ── Health check ────────────────────────────────────────────────────

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Financial Document Analyzer API is running"}


# ── Submit analysis (async via Celery + Redis queue) ────────────────

@app.post("/analyze")
async def analyze_document_endpoint(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights")
):
    """
    Upload a financial document for analysis.
    The request is placed on a Celery queue (Redis broker) and processed by a worker.
    Returns a task_id you can use to poll /status/{task_id}.
    """
    task_id = str(uuid.uuid4())
    file_path = f"data/financial_document_{task_id}.pdf"

    try:
        # Save uploaded file to disk
        os.makedirs("data", exist_ok=True)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Validate query
        if not query:
            query = "Analyze this financial document for investment insights"

        # Create a record in MongoDB (status = "queued")
        create_analysis_record(
            task_id=task_id,
            filename=file.filename,
            query=query.strip(),
        )

        # Send the work to the Celery queue
        analyze_document_task.delay(
            task_id=task_id,
            query=query.strip(),
            file_path=file_path,
        )

        return {
            "status": "queued",
            "task_id": task_id,
            "message": "Your document has been queued for analysis. Poll /status/{task_id} to get the result.",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error queuing financial document: {str(e)}",
        )


# ── Poll analysis status / result ──────────────────────────────────

@app.get("/status/{task_id}")
async def get_analysis_status(task_id: str):
    """Check the status of a queued analysis. Returns the result once completed."""
    record = get_analysis(task_id)
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")

    # Convert datetime objects to strings for JSON serialization
    for key in ("created_at", "updated_at"):
        if key in record and record[key]:
            record[key] = record[key].isoformat()

    return record


# ── List recent analyses ────────────────────────────────────────────

@app.get("/analyses")
async def list_analyses(limit: int = 20):
    """Return the most recent analysis records from MongoDB."""
    records = get_all_analyses(limit=limit)
    for r in records:
        for key in ("created_at", "updated_at"):
            if key in r and r[key]:
                r[key] = r[key].isoformat()
    return records


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)