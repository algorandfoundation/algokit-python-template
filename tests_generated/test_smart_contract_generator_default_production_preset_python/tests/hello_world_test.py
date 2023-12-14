import algokit_utils
import pytest
from algokit_utils import get_localnet_default_account
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient

from smart_contracts.artifacts.hello_world.client import HelloWorldClient


@pytest.fixture(scope="session")
def hello_world_client(
    algod_client: AlgodClient, indexer_client: IndexerClient
) -> HelloWorldClient:
    client = HelloWorldClient(
        algod_client,
        creator=get_localnet_default_account(algod_client),
        indexer_client=indexer_client,
    )

    client.deploy(
        on_schema_break=algokit_utils.OnSchemaBreak.ReplaceApp,
        on_update=algokit_utils.OnUpdate.UpdateApp,
        allow_delete=True,
        allow_update=True,
    )
    return client


def test_says_hello(hello_world_client: HelloWorldClient) -> None:
    result = hello_world_client.hello(name="World")

    assert result.return_value == "Hello, World"
