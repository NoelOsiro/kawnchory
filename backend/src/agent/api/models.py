"""ORM models for dynamic graph configuration tables.

This module centralizes declarative models used by the async
ConfigStore. Models follow a plural table-name convention so
`Base.metadata.create_all` will create the expected tables.
"""
from __future__ import annotations

from sqlalchemy import (
    JSON,
    TIMESTAMP,
    Boolean,
    Column,
    Float,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class SegmentorConfig(Base):
    """_summary_.

    Args:
        Base (_type_): _description_
    """
    __tablename__ = "segmentor_configs"

    segmentor_name = Column(String, primary_key=True)
    enabled = Column(Boolean, nullable=False, default=True)
    metadata_ = Column("metadata", JSON, nullable=False, default={})
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class RoutingRule(Base):
    """_summary_.

    Args:
        Base (_type_): _description_.
    """
    __tablename__ = "routing_rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_node = Column(String, nullable=False)
    condition = Column(JSON, nullable=False)
    target_node = Column(String, nullable=False)
    enabled = Column(Boolean, nullable=False, default=True)
    metadata_ = Column("metadata", JSON, nullable=False, default={})


class NodeConfig(Base):
    """_summary_.

    Args:
        Base (_type_): _description_.
    """
    __tablename__ = "node_configs"

    name = Column(String, primary_key=True)
    enabled = Column(Boolean, nullable=False, default=True)
    metadata_ = Column("metadata", JSON, nullable=False, default={})


class RAGRetrievalConfig(Base):
    """_summary_.

    Args:
        Base (_type_): _description_.
    """
    __tablename__ = "rag_retrieval_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    index_name = Column(String(200))
    vector_db = Column(String(100))
    top_k = Column(Integer, nullable=False, default=5)
    filters = Column(JSON, nullable=False, default={})
    rerank = Column(Boolean, nullable=False, default=False)
    rerank_model = Column(Text)
    enabled = Column(Boolean, nullable=False, default=True)
    metadata_ = Column("metadata", JSON, nullable=False, default={})


class OffersConfig(Base):
    """_summary_.

    Args:
        Base (_type_): _description_.
    """
    __tablename__ = "offers_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(200))
    max_offers = Column(Integer)
    personalization = Column(Boolean, nullable=False, default=False)
    enabled = Column(Boolean, nullable=False, default=True)
    metadata_ = Column("metadata", JSON, nullable=False, default={})


class SafetyConfig(Base):
    """_summary_.

    Args:
        Base (_type_): _description_.
    """
    __tablename__ = "safety_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    enabled = Column(Boolean, nullable=False, default=True)
    toxicity_threshold = Column(Float, nullable=False, default=0.7)
    hallucination_check = Column(Boolean, nullable=False, default=True)
    banned_keywords = Column(JSON, nullable=False, default=[])
    metadata_ = Column("metadata", JSON, nullable=False, default={})


class GenerationConfig(Base):
    """_summary_.

    Args:
        Base (_type_): _description_.
    """
    __tablename__ = "generation_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(200))
    temperature = Column(Float, nullable=False, default=0.7)
    max_tokens = Column(Integer, nullable=False, default=512)
    system_prompt = Column(Text, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=False, default={})


class DeliveryConfig(Base):
    """_summary_.

    Args:
        Base (_type_): _description_.
    """
    __tablename__ = "delivery_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    channel = Column(String(50))
    format = Column(JSON, nullable=False, default={})
    enabled = Column(Boolean, nullable=False, default=True)
    metadata_ = Column("metadata", JSON, nullable=False, default={})


__all__ = [
    "Base",
    "SegmentorConfig",
    "RoutingRule",
    "NodeConfig",
    "RAGRetrievalConfig",
    "OffersConfig",
    "SafetyConfig",
    "GenerationConfig",
    "DeliveryConfig",
]
