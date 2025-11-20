"""General LLM service that selects a Chat LLM implementation by `API_HOST`.

Supported hosts:
- "azure": uses Azure identity + ChatOpenAI (base_url = AZURE_OPENAI_ENDPOINT + "/openai/v1")
- "github": uses GitHub Models via ChatOpenAI configured with `GITHUB_TOKEN` and `GITHUB_BASE_URL`
- "ollama": local Ollama endpoint via ChatOpenAI-compatible base_url
- default: plain OpenAI via ChatOpenAI and `OPENAI_API_KEY`

This factory returns an object suitable for calling like an LLM:
 - Many LangChain wrappers implement `__call__` and/or `generate()`.
 - `callbacks` are forwarded where supported so tracers (LangSmith) can be attached.

The module is defensive: if `ChatOpenAI` isn't available, callers should
handle the fallback or an ImportError will be raised when the adapter cannot
be constructed.
"""
import os
from typing import List

import azure.identity as _azure_identity
from langchain_openai import ChatOpenAI


def get_chat_llm(callbacks: List | None = None):
    """Return a Chat-style LLM instance configured for the selected API host.

    callbacks: optional list to pass to LangChain LLMs (e.g., `[tracer]`).
    """
    api_host = os.getenv("API_HOST", os.getenv("OPENAI_PROVIDER", "github")).lower()

    # Prefer LangChain ChatOpenAI so `callbacks` are supported and LangSmith tracer works
    if ChatOpenAI is None:
        # If ChatOpenAI isn't installed we can't construct LangChain LLMs here.
        raise ImportError("langchain_openai.ChatOpenAI is required to use get_chat_llm")

    if api_host == "azure":
        # Use Azure AD token provider if available
        if _azure_identity is not None:
            token_provider = _azure_identity.get_bearer_token_provider(
                _azure_identity.DefaultAzureCredential(),
                "https://cognitiveservices.azure.com/.default",
            )
            model = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")
            base_url = os.getenv("AZURE_OPENAI_ENDPOINT")
            if base_url and not base_url.endswith("/openai/v1"):
                base_url = base_url.rstrip("/") + "/openai/v1"
            return ChatOpenAI(model=model, base_url=base_url, api_key=token_provider, callbacks=callbacks)
        else:
            # Fallback to api key style if AD not available
            model = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")
            base_url = os.getenv("AZURE_OPENAI_ENDPOINT")
            if base_url and not base_url.endswith("/openai/v1"):
                base_url = base_url.rstrip("/") + "/openai/v1"
            return ChatOpenAI(model=model, base_url=base_url, api_key=os.getenv("AZURE_OPENAI_API_KEY"), callbacks=callbacks)

    if api_host == "github":
        model = os.getenv("GITHUB_LLM_MODEL", os.getenv("GITHUB_MODEL"))
        base_url = os.getenv("GITHUB_BASE_URL", os.getenv("GITHUB_EMBEDDINGS_ENDPOINT", "https://models.inference.ai.azure.com"))
        token = os.getenv("GITHUB_TOKEN")
        return ChatOpenAI(model=model, base_url=base_url, api_key=token, callbacks=callbacks)

    if api_host == "ollama":
        model = os.getenv("OLLAMA_MODEL")
        base_url = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434/v1")
        # Ollama doesn't use an API key in many setups; pass placeholder
        return ChatOpenAI(model=model, base_url=base_url, api_key=os.getenv("OLLAMA_API_KEY", "none"), callbacks=callbacks)

    # Default: OpenAI-style
    model = os.getenv("OPENAI_MODEL", os.getenv("OPENAI_CHAT_MODEL", "gpt-4o"))
    return ChatOpenAI(model=model, api_key=os.getenv("OPENAI_API_KEY"), callbacks=callbacks)
