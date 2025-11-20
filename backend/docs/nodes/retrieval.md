# Retrieval Node

> Placeholder: add design notes, expected inputs, outputs, and examples.

## Purpose

Describe the role of the retrieval node in the workflow.

## Inputs

- State fields expected

## Outputs

- State fields produced/modified

## Implementation checklist

- [ ] Define input schema
- [ ] Implement node logic
- [ ] Add unit tests
- [ ] Add integration tests
- [ ] Add prompts / examples

---

## Retriever Agent (Detailed)

- **Location**: `backend/src/agent/services/retriever.py`
- **Purpose**: Fetch approved content and citations relevant to a customer's context (e.g., product docs). Used for RAG-style generation.
- **API / Contract**:
  - Function: `retrieve_citations(customer: dict) -> list`
  - Input: `customer` object. Retriever may inspect `customer['properties']` (e.g., `product_id`).
  - Output: List of citation objects: `{ 'id': str, 'title': str, 'content': str, 'source': str }`.

### Example

```py
from agent.services.retriever import retrieve_citations

cust = { 'properties': { 'product_id': 'p_101' } }
citations = retrieve_citations(cust)
# citations -> [ { 'id': 'p_101', 'content': '...', 'source': 'product_docs' } ]
```

### Notes

- The scaffold uses `backend/src/agent/services/vector_db.py` simple lookup. Replace with vector search (Pinecone/Azure) for production.
- Keep results deterministic for tests: prefer simple filters and static fixtures in dev.
- Include provenance fields (`source`, `id`) to allow downstream safety and citation display.

### Implementation checklist (suggested)

- [ ] Implement `backend/src/agent/services/retriever.py` with a pluggable lookup function
- [ ] Wire `retrieval_node` to call `retrieve_citations`
- [ ] Add unit tests using stubbed vector DB
- [ ] Add integration test that runs the graph with sample inputs and asserts `retrieved_docs` is populated
- [ ] Document limitations and recommended production replacements
