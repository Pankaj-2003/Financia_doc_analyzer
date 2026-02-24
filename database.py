"""
MongoDB integration for storing analysis results and user data.
Uses pymongo for simplicity.
"""

import os
from datetime import datetime, timezone
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv("env")

# MongoDB connection — defaults to localhost if not set
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.environ.get("MONGO_DB_NAME", "financial_analyzer")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Collections
analyses_collection = db["analyses"]
users_collection = db["users"]


# ── Analysis helpers ────────────────────────────────────────────────

def create_analysis_record(task_id: str, filename: str, query: str) -> dict:
    """Create a new analysis record with status 'queued'."""
    record = {
        "task_id": task_id,
        "filename": filename,
        "query": query,
        "status": "queued",          # queued → processing → completed / failed
        "result": None,
        "error": None,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    analyses_collection.insert_one(record)
    return record


def update_analysis_status(task_id: str, status: str, result: str = None, error: str = None):
    """Update status (and optionally result/error) for an analysis."""
    update_fields = {
        "status": status,
        "updated_at": datetime.now(timezone.utc),
    }
    if result is not None:
        update_fields["result"] = result
    if error is not None:
        update_fields["error"] = error

    analyses_collection.update_one(
        {"task_id": task_id},
        {"$set": update_fields},
    )


def get_analysis(task_id: str) -> dict | None:
    """Retrieve an analysis record by task_id."""
    record = analyses_collection.find_one({"task_id": task_id}, {"_id": 0})
    return record


def get_all_analyses(limit: int = 20) -> list[dict]:
    """Return the most recent analyses."""
    cursor = analyses_collection.find({}, {"_id": 0}).sort("created_at", -1).limit(limit)
    return list(cursor)
