# app/routers/reports.py
from fastapi import APIRouter, Depends
from datetime import datetime, date, time
from typing import Optional, List, Dict, Any
from ..core.security import api_key_guard
from ..services import firebase_client as fb

router = APIRouter(prefix="/reports", tags=["reports"])



@router.get("/late", dependencies=[Depends(api_key_guard)])
async def late_report(day: Optional[str] = None, cutoff: str = "09:00"):
    if day is None:
        target_date = date.today()
    else:
        target_date = date.fromisoformat(day)

    detections = fb.list_detections_for_date(target_date)

    # Parsear cutoff
    h, m = cutoff.split(":")
    cutoff_dt = datetime.combine(target_date, time(hour=int(h), minute=int(m)))

    first_by_person: Dict[str, Dict[str, Any]] = {}

    for det in detections:
        cid = det["client_id"]
        ts = det["timestamp"]  # ya viene como datetime o string

        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts)

        if cid not in first_by_person or ts < first_by_person[cid]["timestamp"]:
            first_by_person[cid] = {
                "timestamp": ts,
                "score": det.get("score"),
            }

    late: List[Dict[str, Any]] = []
    for cid, info in first_by_person.items():
        if cid is None:
            continue
        if info["timestamp"] > cutoff_dt:
            client = fb.read_client(cid) or {}
            late.append({
                "client_id": cid,
                "name": client.get("name"),
                "area": (client.get("meta") or {}).get("area"),  # si guardas área en meta
                "arrival_time": info["timestamp"].isoformat(),
                "delay_minutes": int((info["timestamp"] - cutoff_dt).total_seconds() // 60),
            })

    return {
        "date": target_date.isoformat(),
        "cutoff": cutoff,
        "total_late": len(late),
        "late": late,
    }


@router.get("/daily", dependencies=[Depends(api_key_guard)])
async def daily_summary(day: Optional[str] = None):
    """
    Resumen simple de asistencia de un día:
    - total detecciones
    - personas únicas
    - hora promedio de llegada
    """
    if day is None:
        target_date = date.today()
    else:
        target_date = date.fromisoformat(day)

    detections = fb.list_detections_for_date(target_date)

    if not detections:
        return {
            "date": target_date.isoformat(),
            "total_events": 0,
            "unique_people": 0,
            "avg_first_checkin": None,
        }

    # Agrupar por persona para obtener la primera detección del día
    from collections import defaultdict
    first_by_person: Dict[str, datetime] = {}
    for det in detections:
        cid = det["client_id"]
        ts = det["timestamp"]
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts)
        if cid not in first_by_person or ts < first_by_person[cid]:
            first_by_person[cid] = ts

    # Calcular promedio de hora de llegada
    times = list(first_by_person.values())
    avg_ts = datetime.fromtimestamp(
        sum(t.timestamp() for t in times) / len(times)
    )

    return {
        "date": target_date.isoformat(),
        "total_events": len(detections),
        "unique_people": len(first_by_person),
        "avg_first_checkin": avg_ts.isoformat(),
    }
