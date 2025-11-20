import pytest
import os




@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


def pytest_collection_modifyitems(config, items):
    """Skip LangSmith integration tests when `LANGSMITH_API_KEY` is not set.

    Tests marked with `@pytest.mark.langsmith` require a valid LangSmith API
    key and will fail in environments where the key isn't available. Skip
    them to keep local test runs deterministic.
    """
    if os.getenv("LANGSMITH_API_KEY"):
        return

    skip_marker = pytest.mark.skip(reason="LangSmith API key not configured")
    for item in items:
        if "langsmith" in {m.name for m in item.iter_markers()}:
            item.add_marker(skip_marker)
