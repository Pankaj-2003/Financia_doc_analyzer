"""
Celery worker for processing financial document analysis tasks asynchronously.
Uses Redis as the message broker.
"""

import os
import sys
import io

# Add the project directory to sys.path so Celery workers can find local modules like 'database.py'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Force UTF-8 encoding for Windows console
if sys.stdout and getattr(sys.stdout, "buffer", None):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr and getattr(sys.stderr, "buffer", None):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from celery import Celery
from dotenv import load_dotenv

load_dotenv("env")

# Redis connection — defaults to localhost
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "financial_analyzer",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

# Simple Celery configuration
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    task_track_started=True,
)


@celery_app.task(name="analyze_document_task", bind=True)
def analyze_document_task(self, task_id: str, query: str, file_path: str):
    """
    Background Celery task that runs the CrewAI pipeline and stores
    the result in MongoDB.
    """
    from database import update_analysis_status
    from crewai import Crew, Process
    from agents import financial_analyst, verifier, investment_advisor, risk_assessor, reporting_agent
    from task import (
        analyze_financial_document,
        verification,
        investment_analysis,
        risk_assessment,
        final_report_task,
    )

    try:
        # Mark as processing
        update_analysis_status(task_id, status="processing")

        # Run the crew
        financial_crew = Crew(
            agents=[verifier, financial_analyst, investment_advisor, risk_assessor, reporting_agent],
            tasks=[verification, analyze_financial_document, investment_analysis, risk_assessment, final_report_task],
            process=Process.sequential,
        )
        result = financial_crew.kickoff({"query": query, "file_path": file_path})

        # Save markdown output to outputs/
        os.makedirs("outputs", exist_ok=True)
        output_file = f"outputs/analysis_{task_id}.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(str(result))

        # Store result in MongoDB
        update_analysis_status(task_id, status="completed", result=str(result))

        return {"status": "completed", "task_id": task_id}

    except Exception as exc:
        update_analysis_status(task_id, status="failed", error=str(exc))
        raise

    finally:
        # Clean up uploaded file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
