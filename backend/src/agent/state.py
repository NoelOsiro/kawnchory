from typing import Optional, TypedDict, List, Dict, Any

from langgraph.graph import MessagesState


class State(MessagesState):
    # Input
    user_query: Optional[str] = None

    # Behavioral Signals (used by segmentation and retrieval personalization)
    behavior_summary: Optional[Dict[str, Any]] = None
    customer_profile: Optional[Dict[str, Any]] = None
    rfm_signals: Optional[Dict[str, Any]] = None

    # Segmentation Output
    segment: Optional[str] = None
    segment_metadata: Optional[Dict[str, Any]] = None
    routing_hint: Optional[str] = None

    # Retrieval Output
    retrieved_docs: Optional[List[Dict[str, Any]]] = None
    retrieval_explain: Optional[Dict[str, Any]] = None
    retrieval_settings: Optional[Dict[str, Any]] = None

    # Offers Node Output
    offers: Optional[List[Dict[str, Any]]] = None
    offers_metadata: Optional[Dict[str, Any]] = None

    # Generation Node Output
    generated_message: Optional[str] = None
    generation_metadata: Optional[Dict[str, Any]] = None

    # Safety Node Output
    safety_passed: Optional[bool] = None
    safety_report: Optional[Dict[str, Any]] = None

    # HITL Feedback
    human_feedback: Optional[str] = None

    # Delivery Node Output
    delivered_message: Optional[str] = None
