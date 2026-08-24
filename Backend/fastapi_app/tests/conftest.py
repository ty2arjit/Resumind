import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client() -> TestClient:
    # raise_server_exceptions=False: exercise the actual HTTP response our
    # centralized error handlers (app.core.errors) produce, the same as a
    # real client over the network would see, instead of TestClient
    # re-raising the underlying exception for interactive debugging.
    return TestClient(app, raise_server_exceptions=False)
