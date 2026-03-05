"""Results storage and retrieval — DynamoDB-backed, publicly readable.

Schema (ff-results table):
  result_id  (S, partition key)  UUID
  league_id  (S)
  year       (N)
  through_week (N, optional)
  created_at (S)  ISO-8601
  teams      (S)  JSON string
"""
import json
import os
from datetime import datetime, timezone
from uuid import uuid4

import boto3
from botocore.exceptions import ClientError
from fastapi import APIRouter, HTTPException

_TABLE_NAME = os.environ.get("RESULTS_TABLE", "ff-results")
_dynamodb = None


def _table():
    global _dynamodb
    if _dynamodb is None:
        region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
        _dynamodb = boto3.resource("dynamodb", region_name=region)
    return _dynamodb.Table(_TABLE_NAME)


def _lookup_key(league_id: str, year: int, through_week: int | None) -> str:
    return f"idx#{league_id}#{year}#{through_week or 'full'}"


def find_cached_result(league_id: str, year: int, through_week: int | None) -> str | None:
    """Return the result_id for a previously computed result, or None."""
    resp = _table().get_item(Key={"result_id": _lookup_key(league_id, year, through_week)})
    item = resp.get("Item")
    return item["target_id"] if item else None


def save_result(league_id: str, year: int, through_week: int | None, team_events: list) -> str:
    """Persist calculation results and return the new result_id."""
    result_id = str(uuid4())
    teams = {
        e["team"]: {
            "luck_index": e["luck_index"],
            "pct_worse": e["pct_worse"],
            "pct_better": e["pct_better"],
            "record": e["record"],
            "scores": e["scores"],
            "distribution": e.get("distribution"),
        }
        for e in team_events
    }
    item = {
        "result_id": result_id,
        "league_id": league_id,
        "year": year,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "teams": json.dumps(teams),
    }
    if through_week is not None:
        item["through_week"] = through_week

    _table().put_item(Item=item)
    _table().put_item(Item={
        "result_id": _lookup_key(league_id, year, through_week),
        "target_id": result_id,
    })
    return result_id


router = APIRouter()


@router.get("/results/lookup")
def lookup_result(league_id: str, year: int, through_week: int | None = None):
    """Check if a cached result exists for this league/year/through_week combo."""
    result_id = find_cached_result(league_id, year, through_week)
    if not result_id:
        raise HTTPException(status_code=404, detail="No cached result found")
    return {"result_id": result_id}


@router.get("/results/{result_id}")
def get_result(result_id: str):
    """Return results for a given result_id. No authentication required."""
    try:
        resp = _table().get_item(Key={"result_id": result_id})
    except ClientError as exc:
        raise HTTPException(status_code=500, detail="Storage error") from exc

    item = resp.get("Item")
    if not item:
        raise HTTPException(status_code=404, detail="Result not found")

    return {
        "result_id": result_id,
        "league_id": item["league_id"],
        "year": int(item["year"]),
        "through_week": int(item["through_week"]) if "through_week" in item else None,
        "created_at": item["created_at"],
        "teams": json.loads(item["teams"]),
    }
