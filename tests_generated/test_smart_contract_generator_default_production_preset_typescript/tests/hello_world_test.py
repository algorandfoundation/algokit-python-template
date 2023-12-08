import pytest
from algokit_utils import (
    ApplicationClient,
    ApplicationSpecification,
    get_localnet_default_account,
)
from algosdk.v2client.algod import AlgodClient

from smart_contracts.hello_world import contract as hello_world_contract


@pytest.fixture(scope="session")
def hello_world_app_spec(algod_client: AlgodClient) -> ApplicationSpecification:
    return hello_world_contract.app.build(algod_client)


@pytest.fixture(scope="session")
def hello_world_client(
    algod_client: AlgodClient, hello_world_app_spec: ApplicationSpecification
) -> ApplicationClient:
    client = ApplicationClient(
        algod_client,
        app_spec=hello_world_app_spec,
        signer=get_localnet_default_account(algod_client),
        template_values={"UPDATABLE": 1, "DELETABLE": 1},
    )
    client.create()
    return client


def test_says_hello(hello_world_client: ApplicationClient) -> None:
    result = hello_world_client.call(hello_world_contract.hello, name="World")

    assert result.return_value == "Hello, World"
