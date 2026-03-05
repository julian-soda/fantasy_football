"""DynamoDB-backed session store.

Sessions are stored in the ff-sessions table with a 24-hour TTL.
The session_id is a random token set as an HttpOnly cookie; it never
appears in the response body.
"""
import os
import time
import boto3
from botocore.exceptions import ClientError

_TABLE_NAME = os.environ.get("SESSIONS_TABLE", "ff-sessions")
_dynamodb = None


def _table():
    global _dynamodb
    if _dynamodb is None:
        region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
        _dynamodb = boto3.resource("dynamodb", region_name=region)
    return _dynamodb.Table(_TABLE_NAME)


def get_session(session_id: str) -> dict | None:
    """Return the token dict for session_id, or None if not found / expired."""
    try:
        resp = _table().get_item(Key={"session_id": session_id})
    except ClientError:
        return None
    item = resp.get("Item")
    if not item:
        return None
    # Check TTL manually in case DynamoDB hasn't garbage-collected yet
    if item.get("ttl", 0) < int(time.time()):
        return None

    provider = item.get("provider", "yahoo")
    if provider == "espn":
        return {
            "provider": "espn",
            "espn_s2": item["espn_s2"],
            "swid": item["swid"],
        }

    return {
        "provider": "yahoo",
        "access_token": item["access_token"],
        "refresh_token": item["refresh_token"],
        "guid": item.get("guid", ""),
        "token_time": float(item.get("token_time", 0)),
        "token_type": item.get("token_type", "bearer"),
        "expires_in": int(item.get("expires_in", 3600)),
    }


def set_session(session_id: str, tokens: dict) -> None:
    """Persist tokens for session_id with a 24-hour TTL."""
    provider = tokens.get("provider", "yahoo")
    item: dict = {
        "session_id": session_id,
        "provider": provider,
        "ttl": int(time.time()) + 86400,
    }
    if provider == "espn":
        item["espn_s2"] = tokens["espn_s2"]
        item["swid"] = tokens["swid"]
    else:
        item["access_token"] = tokens["access_token"]
        item["refresh_token"] = tokens["refresh_token"]
        item["guid"] = tokens.get("xoauth_yahoo_guid") or tokens.get("guid", "")
        item["token_time"] = str(tokens.get("token_time", time.time()))
        item["token_type"] = tokens.get("token_type", "bearer")
        item["expires_in"] = tokens.get("expires_in", 3600)
    _table().put_item(Item=item)


def delete_session(session_id: str) -> None:
    """Remove a session (logout)."""
    try:
        _table().delete_item(Key={"session_id": session_id})
    except ClientError:
        pass


def refresh_session(session_id: str, new_tokens: dict) -> None:
    """Update tokens in an existing session after a token refresh."""
    set_session(session_id, new_tokens)
