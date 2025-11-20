import pytest
import sys
import os
import pathlib
import pytest

# Ensure backend/src is on sys.path so `agent.*` imports resolve when
# running tests from the repository root.
HERE = pathlib.Path(__file__).resolve().parent
BACKEND = HERE.parent
SRC = BACKEND / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


