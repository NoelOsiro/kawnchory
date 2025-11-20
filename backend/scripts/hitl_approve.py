#!/usr/bin/env python3
"""CLI for approving/rejecting HITL reviews.

Usage examples:
  # Approve review id 5
  python backend/scripts/hitl_approve.py --id 5 --approve --reviewer automated --notes "OK"

  # Approve all pending
  python backend/scripts/hitl_approve.py --all --approve --reviewer ci --notes "Auto-approved in CI"
"""
import argparse
import sys
from pathlib import Path


def _bootstrap_path():
    # Ensure backend/src is on sys.path so `agent` package imports work
    root = Path(__file__).resolve().parents[1]
    src = root / "src"
    sys.path.insert(0, str(src))


def main(argv=None):
    _bootstrap_path()
    parser = argparse.ArgumentParser(description="Approve/Reject HITL reviews")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--id", type=int, help="Review id to act on")
    group.add_argument("--all", action="store_true", help="Act on all pending reviews")

    parser.add_argument("--approve", action="store_true", help="Approve review(s)")
    parser.add_argument("--reject", action="store_true", help="Reject review(s)")
    parser.add_argument("--reviewer", type=str, default="cli", help="Reviewer name")
    parser.add_argument("--notes", type=str, default=None, help="Optional notes")

    args = parser.parse_args(argv)

    from agent.services import hitl_queue

    if args.all:
        pending = hitl_queue.list_pending()
        ids = [p["id"] for p in pending]
    else:
        ids = [args.id]

    if not ids:
        print("No pending reviews found.")
        return 0

    for rid in ids:
        if args.approve:
            hitl_queue.approve_review(rid, reviewer=args.reviewer, notes=args.notes, result={"approved": True})
            print(f"Approved review {rid}")
        elif args.reject:
            hitl_queue.reject_review(rid, reviewer=args.reviewer, notes=args.notes)
            print(f"Rejected review {rid}")
        else:
            info = hitl_queue.get_review(rid)
            print(info)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
