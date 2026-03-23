import algokit_utils
import pytest
from algokit_utils import (
    AddressWithSigners,
    AlgoAmount,
    AlgorandClient,
)

from smart_contracts.artifacts.hello_world.hello_world_client import (
    HelloWorldClient,
    HelloWorldFactory,
)


@pytest.fixture()
def deployer(algorand_client: AlgorandClient) -> AddressWithSigners:
    account = algorand_client.account.from_environment("DEPLOYER")
    algorand_client.account.ensure_funded_from_environment(
        account_to_fund=account.addr, min_spending_balance=AlgoAmount.from_algo(10)
    )
    return account


@pytest.fixture()
def hello_world_client(
    algorand_client: AlgorandClient, deployer: AddressWithSigners
) -> HelloWorldClient:
    factory = algorand_client.client.get_typed_app_factory(
        HelloWorldFactory, default_sender=deployer.addr
    )

    client, _ = factory.deploy(
        on_schema_break=algokit_utils.OnSchemaBreak.AppendApp,
        on_update=algokit_utils.OnUpdate.AppendApp,
    )
    return client


def test_says_hello(hello_world_client: HelloWorldClient) -> None:
    result = hello_world_client.send.hello(args=("World",))
    assert result.abi_return == "Hello, World"


def test_simulate_says_hello_with_correct_budget_consumed(
    hello_world_client: HelloWorldClient,
) -> None:
    result = (
        hello_world_client.new_group()
        .hello(args=("World",))
        .hello(args=("Jane",))
        .simulate()
    )
    assert result.returns[0].value == "Hello, World"
    assert result.returns[1].value == "Hello, Jane"
    assert result.simulate_response.txn_groups[0].app_budget_consumed < 100
