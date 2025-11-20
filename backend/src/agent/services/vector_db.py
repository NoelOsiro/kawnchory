"""Simple vector DB stub used for development and tests.

Provides `query_by_product_id(product_id)` which returns deterministic
fixtures for test inputs. Replace with real vector search in production.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List

# Small sample index used for deterministic tests and local dev
_SAMPLE_INDEX = {
    "p_101": {
        "id": "p_101",
        "title": "Product 101 Specs",
        "content": "Details about product 101...",
        "source": "product_docs",
    },
    "p_202": {
        "id": "p_202",
        "title": "Product 202 Guide",
        "content": "Usage guidance for product 202...",
        "source": "product_docs",
    },
}


def query_by_product_id(product_id: str) -> List[Dict[str, Any]]:
    """Return citation dicts for `product_id`.

    Behavior:
    - If Azure Search environment variables are set and the Azure SDK is
      available, query Azure Cognitive Search and return results.
    - Otherwise, fall back to the local `_SAMPLE_INDEX` for deterministic tests.
    """
    if not product_id:
        return []

    # Azure Cognitive Search hook (optional)
    # Allow an explicit opt-in/out flag. When unset, fall back to autodetect
    # based on the presence of the Azure config vars.
    use_azure_flag = os.environ.get("USE_AZURE_VECTOR_DB")
    azure_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
    azure_key = os.environ.get("AZURE_SEARCH_KEY")
    azure_index = os.environ.get("AZURE_SEARCH_INDEX")

    azure_config_present = bool(azure_endpoint and azure_key and azure_index)
    use_azure = None
    if use_azure_flag is not None:
        use_azure = use_azure_flag.strip() not in ("0", "false", "False")
    else:
        use_azure = azure_config_present

    if use_azure and azure_config_present:
        try:
            from azure.core.credentials import AzureKeyCredential
            from azure.search.documents import SearchClient

            client = SearchClient(endpoint=azure_endpoint, index_name=azure_index, credential=AzureKeyCredential(azure_key))

            # Prefer direct document lookup if configured key name matches `id`
            try:
                doc = client.get_document(product_id)
                if doc:
                    return [dict(doc)]
            except Exception:
                # If get_document is not available or fails, fall back to search
                pass

            # Fallback: search with an OData filter for id equality
            try:
                results = client.search(search_text="*", filter=f"id eq '{product_id}'")
                out = []
                for r in results:
                    out.append(dict(r))
                if out:
                    return out
            except Exception:
                # Azure query failed — fall through to local index
                pass
        except ImportError:
            # Azure SDK not installed — fall through to local index
            pass
        except Exception:
            # Any other Azure-related error — fall through to local index
            pass

    # Local fallback
    item = _SAMPLE_INDEX.get(product_id)
    return [item] if item else []
