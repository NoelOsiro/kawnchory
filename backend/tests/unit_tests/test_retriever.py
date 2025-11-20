import sys
from pathlib import Path

# Ensure the runtime `src` folder is on sys.path so `agent.*` imports resolve
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from agent.services.retriever import retrieve_citations


def test_retrieve_by_product_id_found():
    customer = {"properties": {"product_id": "p_101"}}
    res = retrieve_citations(customer)
    assert isinstance(res, list)
    assert len(res) == 1
    assert res[0]["id"] == "p_101"


def test_retrieve_by_product_id_not_found():
    customer = {"properties": {"product_id": "unknown"}}
    res = retrieve_citations(customer)
    assert res == []
