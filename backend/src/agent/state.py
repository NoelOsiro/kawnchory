"""State model for the agent pipeline.

This module defines the State class, extending MessagesState, which stores
user input, behavioral signals, segmentation and retrieval outputs, offers,
generation and safety results, human-in-the-loop feedback, and delivery data.
"""

from typing import Any, Dict, List

from langgraph.graph import MessagesState


class State(MessagesState):
    """State model for the agent pipeline.

    Extends MessagesState and stores user input, behavioral signals,
    segmentation and retrieval outputs, offers, generation and safety results,
    human-in-the-loop feedback, and delivery data as attributes.
    """

    # Input
    user_query: str | None = None

    # Behavioral Signals (used by segmentation and retrieval personalization)
    behavior_summary: Dict[str, Any] | None = None
    customer_profile: Dict[str, Any] | None = None
    rfm_signals: Dict[str, Any] | None = None

    # Segmentation Output
    segment: str | None = None
    segment_metadata: Dict[str, Any] | None = None
    routing_hint: str | None = None

    # Retrieval Output
    retrieved_docs: List[Dict[str, Any]] | None = None
    retrieval_explain: Dict[str, Any] | None = None
    retrieval_settings: Dict[str, Any] | None = None

    # Offers Node Output
    offers: List[Dict[str, Any]] | None = None
    offers_metadata: Dict[str, Any] | None = None

    # Generation Node Output
    generated_message: str | None = None
    generation_metadata: Dict[str, Any] | None = None

    # Safety Node Output
    safety_passed: bool | None = None
    safety_report: Dict[str, Any] | None = None

    # HITL Feedback
    human_feedback: str | None = None

    # Delivery Node Output
    delivered_message: str | None = None
