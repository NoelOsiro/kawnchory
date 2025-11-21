"""Pydantic schemas for admin API requests/responses.

This module defines the input (and minimal response) schemas used by the
administrative API endpoints for managing runtime configuration. Schemas are
kept intentionally small and permissive for PATCH-style updates: fields are
optional where the route handlers accept partial updates.

Notes:
- These schemas are simple Pydantic ``BaseModel`` classes used to validate
    incoming JSON payloads and produce serializable dicts for the service
    layer. They intentionally allow ``None`` for fields that are optional in
    patch/update requests.
"""
from __future__ import annotations

from typing import Any, Dict

from pydantic import BaseModel


class RoutingRuleIn(BaseModel):
        """Input schema for creating a routing rule.

        Fields:
        - ``source_node``: Name of the node where the rule originates.
        - ``condition``: JSON-serializable condition object (typically JSONLogic)
            that will be evaluated against the node state to determine if the
            route should be taken.
        - ``target_node``: Name of the node to route to when the condition
            matches.
        - ``enabled``: Optional boolean to create the rule in a disabled state.
            Defaults to ``True`` when omitted.
        """
        source_node: str
        condition: Dict[str, Any]
        target_node: str
        enabled: bool | None = True


class NodeUpdateIn(BaseModel):
    """Partial update schema for a node configuration.

    Both fields are optional so PATCH handlers can accept partial updates.
    - ``enabled`` toggles whether the node is active.
    - ``metadata`` accepts a JSON object with node-specific parameters.
    """
    enabled: bool | None = None
    metadata: Dict[str, Any] | None = None


class GenericIdIn(BaseModel):
    """Simple schema containing an integer id.

    Used by endpoints that accept an object containing an ``id`` field.
    """
    id: int


class RAGUpdateIn(BaseModel):
    """Partial update schema for RAG (retrieval-augmented generation).

    Fields are optional to support patch semantics. Typical fields:
    - ``index_name``: Name of the vector index to query.
    - ``vector_db``: Identifier for the vector DB backend.
    - ``top_k``: Number of nearest neighbours to return.
    - ``filters``: Optional filtering constraints passed to the vector DB.
    - ``rerank`` / ``rerank_model``: Optional reranking configuration.
    - ``enabled``: Toggles the retrieval entry.
    - ``metadata``: Arbitrary JSON for provider-specific options.
    """
    index_name: str | None = None
    vector_db: str | None = None
    top_k: int | None = None
    filters: Dict[str, Any] | None = None
    rerank: bool | None = None
    rerank_model: str | None = None
    enabled: bool | None = None
    metadata: Dict[str, Any] | None = None


class OffersUpdateIn(BaseModel):
    """Partial update schema for offers configuration.

    Fields:
    - ``model_name``: Generation or scoring model used for offers.
    - ``max_offers``: Max number of offers to produce.
    - ``personalization``: Whether to personalize offers.
    - ``enabled``: Toggle feature on/off.
    - ``metadata``: Arbitrary JSON for additional provider options.
    """
    model_name: str | None = None
    max_offers: int | None = None
    personalization: bool | None = None
    enabled: bool | None = None
    metadata: Dict[str, Any] | None = None


class SafetyUpdateIn(BaseModel):
    """Partial update schema for safety-related settings.

    Fields include thresholds and lists used by safety checks. ``banned_keywords``
    is a simple list of strings when present.
    """
    enabled: bool | None = None
    toxicity_threshold: float | None = None
    hallucination_check: bool | None = None
    banned_keywords: list | None = None
    metadata: Dict[str, Any] | None = None


class GenerationUpdateIn(BaseModel):
    """Partial update schema for generation parameters.

    Typical fields control model selection and decoding parameters.
    """
    model_name: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    system_prompt: str | None = None
    metadata: Dict[str, Any] | None = None


class DeliveryUpdateIn(BaseModel):
    """Partial update schema for delivery configuration.

    Fields:
    - ``channel``: Delivery channel identifier (e.g., "email", "sms").
    - ``format``: Delivery format options (JSON-serializable).
    - ``enabled``: Toggle delivery integration.
    - ``metadata``: Provider-specific options.
    """
    channel: str | None = None
    format: Dict[str, Any] | None = None
    enabled: bool | None = None
    metadata: Dict[str, Any] | None = None
