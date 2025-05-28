"""API endpoints for Echo agent operations and log search."""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from io import StringIO
import csv

from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from interface.api.v1.endpoints.metrics import get_redis_client
from interface.api.v1.endpoints.system import _call_orchestrator

logger = logging.getLogger(__name__)
router = APIRouter()


class EchoPayload(BaseModel):
    message: str


class EchoSearchFilters(BaseModel):
    """Advanced search filters for Echo logs."""
    query: Optional[str] = None
    level: Optional[str] = None
    agent_id: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    limit: int = 100
    offset: int = 0
    sort_order: str = "desc"  # "asc" or "desc"
    include_payload: bool = True


@router.post("/", summary="Send message to Echo agent", response_model=Dict[str, str])
def send_echo(payload: EchoPayload) -> Dict[str, str]:
    """Proxy a message to the Echo agent via the orchestrator."""
    command_payload = {
        "agent_name": "echo_agent",
        "message": payload.message,
    }
    response = _call_orchestrator(
        action="dispatch_agent_message", payload=command_payload
    )
    content = response.get("response")
    if content is None:
        raise HTTPException(status_code=502, detail="No response from orchestrator")
    return {"echo": content}


@router.get("/search", summary="Search Echo events with advanced filtering")
def search_echo(
    query: Optional[str] = Query(None, description="Text search in log content"),
    level: Optional[str] = Query(None, description="Log level filter (INFO, DEBUG, ERROR, etc.)"),
    agent_id: Optional[str] = Query(None, description="Filter by specific agent ID"),
    start_time: Optional[str] = Query(None, description="Start time (ISO format)"),
    end_time: Optional[str] = Query(None, description="End time (ISO format)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order by timestamp"),
    include_payload: bool = Query(True, description="Include full payload in results"),
    format: str = Query("json", regex="^(json|csv)$", description="Response format"),
) -> Any:
    """Search logged Echo events with advanced filtering and export options."""
    client = get_redis_client()
    if client is None:
        if format == "csv":
            return Response(content="", media_type="text/csv")
        return {"events": [], "total": 0, "next_offset": None}

    # Parse time filters
    start_ts = None
    end_ts = None
    if start_time:
        try:
            start_ts = datetime.fromisoformat(start_time.replace('Z', '+00:00')).timestamp()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_time format")
    if end_time:
        try:
            end_ts = datetime.fromisoformat(end_time.replace('Z', '+00:00')).timestamp()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_time format")

    # Determine search strategy based on filters
    search_key = None
    if level:
        search_key = f"echo:by_level:{level}"
    elif agent_id:
        search_key = f"echo:by_agent:{agent_id}"

    # Get raw events from Redis
    if search_key and (start_ts is not None or end_ts is not None):
        # Use sorted set with timestamp range
        start_score = start_ts if start_ts is not None else float("-inf")
        end_score = end_ts if end_ts is not None else float("+inf")
        raw_events = client.zrangebyscore(search_key, start_score, end_score)
    elif search_key:
        # Use sorted set without timestamp filter
        raw_events = client.zrange(search_key, 0, -1)
    else:
        # Fall back to main events list
        raw_events = client.lrange("echo:events", 0, -1)

    # Parse and filter events
    events = []
    total_count = 0
    
    for item in raw_events:
        try:
            data = json.loads(item)
        except json.JSONDecodeError:
            continue
            
        total_count += 1
        
        # Apply filters
        if agent_id and data.get("agent_id") != agent_id:
            continue
        if level and data.get("level") != level:
            continue
        if query and query.lower() not in json.dumps(data).lower():
            continue
            
        # Apply time filters if not already filtered by Redis
        if start_ts is not None or end_ts is not None:
            event_ts = data.get("timestamp", 0)
            if start_ts is not None and event_ts < start_ts:
                continue
            if end_ts is not None and event_ts > end_ts:
                continue
        
        events.append(data)

    # Sort events
    events.sort(key=lambda x: x.get("timestamp", 0), reverse=(sort_order == "desc"))
    
    # Apply pagination
    paginated_events = events[offset:offset + limit]
    
    # Prepare response data
    if not include_payload:
        for event in paginated_events:
            event.pop("payload", None)
    
    # Format response
    if format == "csv":
        return _export_events_csv(paginated_events)
    
    next_offset = offset + len(paginated_events) if len(events) > offset + limit else None
    
    return {
        "events": paginated_events,
        "total": len(events),
        "returned": len(paginated_events),
        "offset": offset,
        "next_offset": next_offset,
        "filters_applied": {
            "query": query,
            "level": level,
            "agent_id": agent_id,
            "start_time": start_time,
            "end_time": end_time,
        }
    }


@router.get("/stream", summary="Real-time Echo event stream")
async def stream_echo_events(
    level: Optional[str] = Query(None, description="Filter by log level"),
    agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
):
    """Stream Echo events in real-time using Server-Sent Events."""
    async def event_generator():
        client = get_redis_client()
        if client is None:
            yield "data: {\"error\": \"Redis not available\"}\n\n"
            return
            
        # Subscribe to Echo events channel
        pubsub = client.pubsub()
        pubsub.subscribe("echo:events")
        
        try:
            for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        event_data = json.loads(message["data"])
                        
                        # Apply filters
                        if level and event_data.get("level") != level:
                            continue
                        if agent_id and event_data.get("agent_id") != agent_id:
                            continue
                            
                        yield f"data: {json.dumps(event_data)}\n\n"
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logger.error(f"Error in event stream: {e}")
            yield f"data: {{\"error\": \"Stream error: {str(e)}\"}}\n\n"
        finally:
            pubsub.close()
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )


@router.get("/stats", summary="Get Echo logging statistics")
def get_echo_stats() -> Dict[str, Any]:
    """Get statistics about Echo logging activity."""
    client = get_redis_client()
    if client is None:
        return {"error": "Redis not available"}
    
    try:
        # Get total event count
        total_events = client.llen("echo:events")
        
        # Get events by level
        levels = ["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"]
        level_counts = {}
        for level in levels:
            level_counts[level] = client.zcard(f"echo:by_level:{level}")
        
        # Get recent activity (last hour)
        one_hour_ago = (datetime.now() - timedelta(hours=1)).timestamp()
        recent_events = 0
        
        # Sample recent events to count activity
        recent_raw = client.lrange("echo:events", 0, 100)
        for item in recent_raw:
            try:
                data = json.loads(item)
                if data.get("timestamp", 0) > one_hour_ago:
                    recent_events += 1
            except json.JSONDecodeError:
                continue
        
        # Get active agents
        active_agents = set()
        agent_keys = client.keys("echo:by_agent:*")
        for key in agent_keys:
            agent_id = key.split(":")[-1]
            if client.zcard(key) > 0:
                active_agents.add(agent_id)
        
        return {
            "total_events": total_events,
            "events_by_level": level_counts,
            "recent_activity": {
                "last_hour": recent_events,
                "timestamp": datetime.now().isoformat(),
            },
            "active_agents": list(active_agents),
            "agent_count": len(active_agents),
        }
    except Exception as e:
        logger.error(f"Error getting Echo stats: {e}")
        return {"error": str(e)}


@router.delete("/clear", summary="Clear Echo event logs")
def clear_echo_logs(
    level: Optional[str] = Query(None, description="Clear only specific level"),
    agent_id: Optional[str] = Query(None, description="Clear only specific agent"),
    older_than_hours: Optional[int] = Query(None, description="Clear events older than N hours"),
) -> Dict[str, Any]:
    """Clear Echo event logs with optional filtering."""
    client = get_redis_client()
    if client is None:
        return {"error": "Redis not available"}
    
    try:
        cleared_count = 0
        
        if older_than_hours:
            # Clear old events based on timestamp
            cutoff_time = (datetime.now() - timedelta(hours=older_than_hours)).timestamp()
            
            if level:
                key = f"echo:by_level:{level}"
                cleared_count = client.zremrangebyscore(key, 0, cutoff_time)
            elif agent_id:
                key = f"echo:by_agent:{agent_id}"
                cleared_count = client.zremrangebyscore(key, 0, cutoff_time)
            else:
                # Clear from main list (more complex for list structure)
                events = client.lrange("echo:events", 0, -1)
                to_remove = []
                for item in events:
                    try:
                        data = json.loads(item)
                        if data.get("timestamp", 0) < cutoff_time:
                            to_remove.append(item)
                    except json.JSONDecodeError:
                        continue
                
                for item in to_remove:
                    client.lrem("echo:events", 1, item)
                    cleared_count += 1
        else:
            # Clear all events for specific filters
            if level:
                key = f"echo:by_level:{level}"
                cleared_count = client.delete(key)
            elif agent_id:
                key = f"echo:by_agent:{agent_id}"
                cleared_count = client.delete(key)
            else:
                # Clear all events
                cleared_count = client.delete("echo:events")
                # Also clear all indexed keys
                for key in client.keys("echo:by_*"):
                    client.delete(key)
        
        return {
            "cleared_count": cleared_count,
            "filters": {
                "level": level,
                "agent_id": agent_id,
                "older_than_hours": older_than_hours,
            },
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error clearing Echo logs: {e}")
        return {"error": str(e)}


def _export_events_csv(events: List[Dict[str, Any]]) -> StreamingResponse:
    """Export events as CSV format."""
    def generate_csv():
        output = StringIO()
        if not events:
            yield ""
            return
            
        # Determine CSV columns from first event
        fieldnames = ["timestamp", "level", "agent_id", "message"]
        if events and "payload" in events[0]:
            # Add payload fields
            payload_keys = set()
            for event in events:
                if "payload" in event and isinstance(event["payload"], dict):
                    payload_keys.update(event["payload"].keys())
            fieldnames.extend(sorted(payload_keys))
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for event in events:
            row = {
                "timestamp": datetime.fromtimestamp(event.get("timestamp", 0)).isoformat(),
                "level": event.get("level", ""),
                "agent_id": event.get("agent_id", ""),
                "message": event.get("message", ""),
            }
            
            # Add payload fields
            if "payload" in event and isinstance(event["payload"], dict):
                for key, value in event["payload"].items():
                    row[key] = str(value) if value is not None else ""
            
            writer.writerow(row)
        
        yield output.getvalue()
    
    return StreamingResponse(
        generate_csv(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=echo_logs.csv"}
    )
