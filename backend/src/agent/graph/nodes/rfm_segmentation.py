"""RFM-based segmentation wrapper.

Delegates to `segmentation_node` for now; specialized RFM logic can be added
here later (e.g., recency/monetary/frequency specific bucketing).
"""
from typing import Any, Dict, Optional


def _safe_int(v: Any, default: int = 0) -> int:
    try:
        return int(v)
    except Exception:
        return default


async def rfm_seg(state: Any, runtime: Any = None) -> Any:
    """RFM-based segmentation.

    Expects `rfm_signals` with `recency_days`, `frequency`, `monetary`.
    """
    if isinstance(state, dict):
        rfm = state.get("rfm_signals") or {}
    else:
        rfm = getattr(state, "rfm_signals", {}) or {}

    recency = _safe_int(rfm.get("recency_days", 9999))
    frequency = _safe_int(rfm.get("frequency", 0))
    monetary = float(rfm.get("monetary", 0.0) or 0.0)

    reasons = []
    routing_hint: Optional[str] = None

    if monetary > 1000 and recency < 90:
        segment = "high_value_active"
        reasons.append(f"monetary={monetary}")
        routing_hint = "generation"
    elif recency > 180:
        segment = "win_back"
        reasons.append(f"recency_days={recency}")
        routing_hint = "offers"
    elif frequency >= 5:
        segment = "loyal"
        reasons.append(f"frequency={frequency}")
        routing_hint = "offers"
    else:
        segment = "rfm_unknown"
        reasons.append("no_rfm_match")

    segment_metadata: Dict[str, Any] = {"recency_days": recency, "frequency": frequency, "monetary": monetary}

    result = {
        "segment": segment,
        "reasons": reasons,
        "segment_metadata": segment_metadata,
        "routing_hint": routing_hint,
    }

    try:
        if isinstance(state, dict):
            state.update(result)
            return state
        else:
            for k, v in result.items():
                try:
                    setattr(state, k, v)
                except Exception:
                    pass
            return state
    except Exception:
        return result
