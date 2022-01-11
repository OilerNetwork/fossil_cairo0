import asyncio
import pytest
from typing import NamedTuple

from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.testing.starknet import Starknet

class TestsDeps(NamedTuple):
    starknet: Starknet
    math_contract: StarknetContract

@pytest.fixture(scope='module')
def event_loop():
    return asyncio.new_event_loop()

async def setup():
    starknet = await Starknet.empty()
    math_contract = await starknet.deploy(source="contracts/starknet/test/TestMathCmp.cairo", cairo_path=["contracts"])
    return TestsDeps(
        starknet=starknet,
        math_contract=math_contract
    )

@pytest.fixture(scope='module')
async def factory():
    return await setup()

@pytest.mark.asyncio
async def test_is_le(factory):
    starknet, math_contract = factory

    a = 0
    b = 0

    call = await math_contract.test_is_le(a, b).call()
    result = call.result.res

    assert result == int(a < b)