from __future__ import annotations

import os
from typing import Any, Dict, List

from agent.state import State

try:
    from langchain_openai import AzureOpenAI, OpenAI
except Exception:
    AzureOpenAI = None
    OpenAI = None

from langgraph.runtime import Runtime

try:
    # optional centralized LLM helper used in some environments
    from services.llm_service import get_chat_llm
except Exception:
    get_chat_llm = None

# Optional tracer used for LLM callbacks (may be provided by runtime)
tracer = None




def _call_llm_for_variants(name: str, seg_label: str, citation_text: str) -> List[Dict[str, Any]]:
    """Attach the LangSmith tracer via callbacks.

    This function is intentionally defensive: it only runs when an LLM
    class is available and the environment provides the required API key.
    Otherwise it raises or returns an empty list and the caller can fall
    back to deterministic output.
    """
    # Prefer Azure if configured
    try:
        # Use the centralized LLM service which returns a Chat-style LLM
        # configured for the selected `API_HOST`. This ensures callbacks
        # (tracing) are wired consistently across providers.
        try:
            llm = get_chat_llm(callbacks=[tracer] if tracer else None)
        except Exception:
            llm = None

        # Fallback to direct OpenAI/Azure wrappers if needed
        if llm is None and AzureOpenAI and os.getenv("AZURE_OPENAI_API_KEY"):
            llm = AzureOpenAI(
                azure_deployment=os.getenv("AZURE_OPENAI_COMPLETION_DEPLOYMENT"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                callbacks=[tracer] if tracer else None,
            )
        elif llm is None and OpenAI and os.getenv("OPENAI_API_KEY"):
            llm = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                callbacks=[tracer] if tracer else None,
            )
        # Previous GitHub-specific logic is now handled by get_chat_llm
        # or the fallbacks above. If we still don't have an llm, abort.
        if llm is None:
            return []

        prompt = (
            f"Create two short email variants (id, subject, body, meta.type) for a user named {name} "
            f"about {seg_label}. Include the citation: {citation_text}\n\nRespond in plain text."
        )

        # Many LangChain LLM wrappers implement __call__ to return text.
        # We wrap in try/except to avoid breaking runtime if the API surface
        # differs in the environment.
        try:
            response = llm(prompt)
            text = str(response)
        except Exception:
            # Best-effort: try generate API with a few message shapes.
            try:
                # Some LangChain versions accept a simple list of strings
                res = llm.generate([prompt])
                # attempt to extract text from the generations
                if hasattr(res, "generations") and res.generations:
                    text = getattr(res.generations[0][0], "text", str(res.generations[0][0]))
                else:
                    text = str(res)
            except Exception:
                # Try structured chat message form (works with ChatOpenAI wrappers)
                try:
                    # Prefer langchain_core message class, fall back to langchain.schema HumanMessage
                    try:
                        from langchain_core.messages.chat import (
                            ChatMessage as _ChatMessage,  # type: ignore
                        )
                        msg = _ChatMessage(content=prompt, role="user")
                    except Exception:
                        try:
                            from langchain.schema import (
                                HumanMessage as _HumanMessage,  # type: ignore
                            )
                            msg = _HumanMessage(content=prompt)
                        except Exception:
                            # Give up: we cannot construct a chat message in this environment
                            return []

                    messages = [[msg]]
                    res = llm.generate(messages)
                    if hasattr(res, "generations") and res.generations:
                        text = getattr(res.generations[0][0], "text", str(res.generations[0][0]))
                    else:
                        text = str(res)
                except Exception:
                    return []

        # Return a single LLM-derived variant as an example. In production
        # you'd parse structured output (JSON) from the LLM.
        return [
            {
                "id": "LLM-1",
                "subject": f"LLM suggestion about {seg_label}",
                "body": text,
                "meta": {"type": "llm"},
            }
        ]
    except Exception:
        return []


async def generation_node(state: State | Dict[str, Any], runtime: Runtime) -> Dict[str, Any]:
    """Generate natural language message from offers and retrieved content.

    This simple generator is deterministic and safe for unit tests. In
    production, replace with an LLM or a controlled prompt chain.
    """
    if isinstance(state, dict):
        segment = state.get("segment")
        offers = state.get("offers") or []
    else:
        segment = getattr(state, "segment", None)
        offers = getattr(state, "offers", None) or []

    # Build a simple customer dict for the generator API
    if isinstance(state, dict):
        customer = state.get("customer", {})
    else:
        customer = getattr(state, "customer", {}) or {}

    # Try to use any retrieved citations attached to state (if present)
    if isinstance(state, dict):
        citations = state.get("citations") or []
    else:
        citations = getattr(state, "citations", None) or []

    # Build segment dict
    seg = segment if isinstance(segment, dict) else {"label": segment}

    # Generate variants (LLM-backed if enabled, otherwise deterministic)
    variants = generate_variants(customer=customer, segment=seg, citations=citations)

    # Keep backward-compatible single message field: choose first variant body
    if variants:
        message = variants[0].get("body") or f"Here are options for your segment ({seg.get('label')})."
    else:
        message = f"Here are the best options we found for you ({seg.get('label')})."

    return {
        "generated_message": message,
        "generation_metadata": {"offers_count": len(offers), "variants_count": len(variants), "variants": variants},
    }


def generate_variants(customer: Dict[str, Any], segment: Dict[str, Any], citations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate A/B/n variants for a customer and segment.

    - Tries to call an LLM path when `USE_LLM_GENERATOR` is set to a truthy value
      and optional LLM helpers are available.
    - Otherwise falls back to deterministic templated variants.

    Each variant includes `meta.citations` so downstream safety checks can
    reference sources.
    """
    # Normalize inputs
    name = (customer.get("name") or "Customer") if isinstance(customer, dict) else "Customer"
    seg_label = (segment.get("label") or str(segment)) if isinstance(segment, dict) else str(segment)

    # If LLM is requested and helper exists, attempt LLM generation
    use_llm = os.getenv("USE_LLM_GENERATOR", "false").lower() in ("1", "true", "yes")
    if use_llm:
        # Build a single citation text blob for the LLM prompt
        citation_text = "\n".join([c.get("text", "") for c in citations]) if citations else ""
        try:
            llm_variants = _call_llm_for_variants(name, seg_label, citation_text)
            if llm_variants:
                # Attach citations into meta for each variant
                for v in llm_variants:
                    v.setdefault("meta", {})
                    v["meta"].setdefault("citations", citations)
                return llm_variants
        except Exception:
            # Silence LLM failures and fall back
            pass

    # Deterministic fallback: generate two simple variants A/B
    variants: List[Dict[str, Any]] = []
    for idx, vid in enumerate(["A", "B", "C"][:2]):
        subject = f"Special options for {seg_label} — variant {vid}"
        body_lines = [f"Hi {name},", "", f"We looked at options for the segment: {seg_label}.", ""]
        # include a short list of citations (titles or snippets)
        if citations:
            body_lines.append("Sources:")
            for c in citations[:3]:
                title = c.get("title") or c.get("id") or c.get("source", "source")
                snippet = c.get("text", "")[:160]
                body_lines.append(f"- {title}: {snippet}")
            body_lines.append("")

        body_lines.append("Best regards,")
        body_lines.append("Your Team")
        body = "\n".join(body_lines)

        variants.append({
            "id": vid,
            "subject": subject,
            "body": body,
            "meta": {"segment": seg_label, "citations": citations},
        })

    return variants
