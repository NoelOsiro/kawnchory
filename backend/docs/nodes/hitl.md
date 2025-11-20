# Human-in-the-loop (HITL) Node

> Placeholder: add design notes, expected inputs, outputs, and examples.

## Purpose

Describe the role of the HITL node in the workflow.

Purpose

- Entrypoint for human review when safety checks fail or policy requires manual approval.

Behavior (stub)

- This repository contains a deterministic stub `hitl_node` that simulates a human review
 and returns `human_review` with `approved` and `notes`. Replace with an integration
 to a review UI, ticketing system, or human-in-the-loop review queue in production.

Outputs

- `human_review`: dict `{approved: bool, notes: str, reasons: list}`

Notes

- Keep human review as an explicit, auditable step; wire to a queue or third-party tool for real workflows.

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
