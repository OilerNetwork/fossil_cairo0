import pytest
import asyncio
from typing import NamedTuple

from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.testing.starknet import Starknet


class TestsDeps(NamedTuple):
    starknet: Starknet
    bitset_contract: StarknetContract

@pytest.fixture(scope='module')
def event_loop():
    return asyncio.new_event_loop()

async def setup():
    starknet = await Starknet.empty()
    bitset_contract = await starknet.deploy(source="contracts/starknet/test/TestBitset.cairo", cairo_path=["contracts"])
    return TestsDeps(
        starknet=starknet,
        bitset_contract=bitset_contract
    )

@pytest.fixture(scope='module')
async def factory():
    return await setup()

@pytest.mark.asyncio
async def test_bitset4(factory):
    starknet, bitset_contract = factory

    bitset = int('0001', 2)

    get_bitset_position_call = await bitset_contract.test_bitset4_get(bitset, 4).call()
    assert get_bitset_position_call.result.res == 1

@pytest.mark.asyncio
async def test_bitset6(factory):
    starknet, bitset_contract = factory

    bitset = int('000001', 2)
    get_bitset_position_call = await bitset_contract.test_bitset6_get(bitset, 6).call()
    assert get_bitset_position_call.result.res == 1

@pytest.mark.asyncio
async def test_bitset(factory):
    starknet, bitset_contract = factory

    bitset = int('0000001', 2)
    get_bitset_position_call = await bitset_contract.test_bitset_get(bitset, 7, 7).call()
    assert get_bitset_position_call.result.res == 1