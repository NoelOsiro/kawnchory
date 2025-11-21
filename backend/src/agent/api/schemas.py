"""Pydantic schemas for admin API requests/responses."""
from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel


class RoutingRuleIn(BaseModel):
    source_node: str
    condition: Dict[str, Any]
    target_node: str
    enabled: bool | None = True


class NodeUpdateIn(BaseModel):
    enabled: bool | None = None
    metadata: Dict[str, Any] | None = None


class GenericIdIn(BaseModel):
    id: int


class RAGUpdateIn(BaseModel):
    index_name: str | None = None
    vector_db: str | None = None
    top_k: int | None = None
    filters: Dict[str, Any] | None = None
    rerank: bool | None = None
    rerank_model: str | None = None
    enabled: bool | None = None
    metadata: Dict[str, Any] | None = None


class OffersUpdateIn(BaseModel):
    model_name: str | None = None
    max_offers: int | None = None
    personalization: bool | None = None
    enabled: bool | None = None
    metadata: Dict[str, Any] | None = None


class SafetyUpdateIn(BaseModel):
    enabled: bool | None = None
    toxicity_threshold: float | None = None
    hallucination_check: bool | None = None
    banned_keywords: list | None = None
    metadata: Dict[str, Any] | None = None


class GenerationUpdateIn(BaseModel):
    model_name: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    system_prompt: str | None = None
    metadata: Dict[str, Any] | None = None


class DeliveryUpdateIn(BaseModel):
    channel: str | None = None
    format: Dict[str, Any] | None = None
    enabled: bool | None = None
    metadata: Dict[str, Any] | None = None
