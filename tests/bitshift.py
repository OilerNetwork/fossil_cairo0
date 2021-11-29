from typing import NamedTuple
import pytest
from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.testing.starknet import Starknet

class TestsDeps(NamedTuple):
    starknet: Starknet
    bitshift_contract: StarknetContract

async def setup():
    starknet = await Starknet.empty()
    bitshift_contract = await starknet.deploy(source="contracts/starknet/test/TestBitshift.cairo", cairo_path=["contracts"])
    return TestsDeps(
        starknet=starknet,
        bitshift_contract=bitshift_contract
    )

@pytest.mark.asyncio
async def test_bitshift_right_8():
    starknet, bitshift_contract = await setup()

    right_bitshift_call = await bitshift_contract.test_bitshift_right(4, 1).call()

    print(right_bitshift_call.result)

@pytest.mark.asyncio
async def test_bitshift_left_8():
    starknet, bitshift_contract = await setup()

    right_bitshift_call = await bitshift_contract.test_bitshift_left(4, 1).call()

    print(right_bitshift_call.result)