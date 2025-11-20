# Offers Node

Purpose
- Convert retrieval results and segmentation into a small set of structured offers for message generation and delivery.

Inputs
- `retrieved_docs`: list of documents (dicts) from the retriever
- `segment`: segmentation label (string)

Outputs
- `offers`: list of offer dicts with `product_id`, `title`, `price`, `discount`, `final_price`
- `offers_count`: number of offers
- `routing_hint`: recommended next node (`generation`)

Behavior
- Deterministic selection of the top N (3) results.
- Simple discount rules based on `segment` for local/dev testing. Production logic should consult pricing rules and inventory.

Testing
- Unit tests exercise discount rules and empty retrieval behavior.
# Offers Node

> Placeholder: add design notes, expected inputs, outputs, and examples.

## Purpose

Describe the role of the offers node in the workflow.

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
