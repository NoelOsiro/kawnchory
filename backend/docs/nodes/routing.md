# Routing Rules

This document explains the admin-configurable routing rules and how to write
conditions.

Key points

- Routing rules live in the `routing_rules` DB table and are exposed via the
  admin API at `POST /admin/routing` and `GET /admin/routing`.
- Each rule has: `source_node`, `condition`, `target_node`, `enabled` and
  optional `metadata`.
- Conditions are expressed in JSONLogic (recommended) or simple field equality
  maps as a fallback.

Examples

A) Simple equality (fallback)

A rule that sends segment `x` to `offers` after segmentation:

{
  "source_node": "seg",
  "condition": {"segment": "x"},
  "target_node": "offers",
  "enabled": true
}

B) Nested key using JSONLogic

Match when `customer.name` equals "Alice":

{
  "source_node": "segment_merge",
  "condition": {"==": [{"var": "customer.name"}, "Alice"]},
  "target_node": "retrieval",
  "enabled": true
}

C) Existence check

Match when `customer.email` exists (is not null):

{
  "source_node": "segment_merge",
  "condition": {"!=": [{"var": "customer.email"}, null]},
  "target_node": "retrieval",
  "enabled": true
}

D) Complex JSONLogic (AND / OR)

Send to `retrieval` if the segment contains "intent" or if `user_query` is present:

{
  "source_node": "segment_merge",
  "condition": {"or": [
      {"in": ["intent", {"var": "segment"}]},
      {"var": "user_query"}
  ]},
  "target_node": "retrieval",
  "enabled": true
}

Notes

- We use the `jsonlogic` Python package when available to evaluate expressions.
- If `jsonlogic` is not installed, the system falls back to a simple
  nested-key equality matcher (e.g., `{ "segment": "x" }`).
- Source node aliases: `seg` maps to `segment_merge`, `inspection` maps to
  `context_inspection` for convenience.

If you want richer predicates (regex, ranges, fuzzy matching), we can extend
support or normalize expressions into JSONLogic with custom operators.
