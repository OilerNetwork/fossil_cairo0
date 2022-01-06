import pytest
import asyncio
from typing import NamedTuple

from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.testing.starknet import Starknet
from starkware.starkware_utils.error_handling import StarkException

from utils.Signer import Signer
from utils.create_account import create_account


class TestsDeps(NamedTuple):
    starknet: Starknet
    facts_registry: StarknetContract
    account: StarknetContract
    signer: Signer

@pytest.fixture(scope='module')
def event_loop():
    return asyncio.new_event_loop()

async def setup():
    starknet = await Starknet.empty()
    facts_registry = await starknet.deploy(source="contracts/starknet/FactsRegistry.cairo", cairo_path=["contracts"])
    account, signer = await create_account(starknet)

    return TestsDeps(
        starknet=starknet,
        facts_registry=facts_registry,
        account=account,
        signer=signer)

@pytest.fixture(scope='module')
async def base_factory():
    return await setup()


@pytest.mark.asyncio
async def test_initializer(base_factory):
    starknet, facts_registry, account, signer = base_factory

