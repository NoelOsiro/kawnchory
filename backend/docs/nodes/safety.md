# Safety Node

> Placeholder: add design notes, expected inputs, outputs, and examples.

## Purpose

Describe the role of the safety node in the workflow.

Purpose

- Run deterministic safety checks on generated messages and offers during local development and tests.

Checks performed

- Banned-keyword scan on `generated_message` (simple list for deterministic tests).
- Offers sanity checks: `discount` bounds (0-0.5) and `final_price` non-negative.

Outputs

- `safety_passed`: boolean
- `safety_report`: dict with `reasons` and `offending` details
- `routing_hint`: `hitl` when review is recommended

Notes

- This is intentionally simple to keep tests deterministic. Replace with a policy/classifier in production.

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
