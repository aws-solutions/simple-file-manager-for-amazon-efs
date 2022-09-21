import pytest
from chalice.test import Client
from botocore.stub import Stubber

@pytest.fixture(autouse=True)
def mock_env_variables(monkeypatch):
    monkeypatch.syspath_prepend('../../source/api/')
    monkeypatch.setenv("stackPrefix", "testStackPrefix")
    monkeypatch.setenv("botoConfig", '{"user_agent_extra": "AwsSolution/SO0145/vX.X.X"}')

@pytest.fixture
def test_client(mock_env_variables):
    from app import app
    with Client(app) as client:
        yield client

@pytest.fixture
def efs_client_stub(mock_env_variables):
    from app import EFS
    with Stubber(EFS) as stubber:
        yield stubber
        stubber.assert_no_pending_responses()

@pytest.fixture
def cfn_client_stub(mock_env_variables):
    from app import CFN
    with Stubber(CFN) as stubber:
        yield stubber
        stubber.assert_no_pending_responses()

@pytest.fixture
def lambda_client_stub(mock_env_variables):
    from app import SERVERLESS
    with Stubber(SERVERLESS) as stubber:
        yield stubber
        stubber.assert_no_pending_responses()