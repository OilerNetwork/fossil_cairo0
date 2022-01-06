import pytest
import asyncio
from typing import NamedTuple

from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.testing.starknet import Starknet

from utils.types import Data

class TestsDeps(NamedTuple):
    starknet: Starknet
    address_contract: StarknetContract

@pytest.fixture(scope='module')
def event_loop():
    return asyncio.new_event_loop()

async def setup():
    starknet = await Starknet.empty()
    address_contract = await starknet.deploy(source="contracts/starknet/test/TestAddressLib.cairo", cairo_path=["contracts"])
    return TestsDeps(
        starknet=starknet,
        address_contract=address_contract
    )

@pytest.fixture(scope='module')
async def factory():
    return await setup()

example_addr = '0x9cB1e11D87013e70038f80381A70b6a6C4eCf519'

@pytest.mark.asyncio
async def test_address_words64_to_160bit(factory):
    starknet, address_contract = factory

    input = Data.from_hex(example_addr).to_ints().values

    assert len(input) == 3

    address_to_160bit_call = await address_contract.test_address_words64_to_160bit(
        input[0],
        input[1],
        input[2]
    ).call()

    output = address_to_160bit_call.result.res
    expected_output = int(example_addr[2:], 16)

    assert output == expected_output

@pytest.mark.asyncio
async def test_address_160bit_to_words64(factory):
    starknet, address_contract = factory

    address_to_words64_call = await address_contract.test_address_160bit_to_words64(
        int(example_addr[2:], 16)
    ).call()
    output = list(address_to_words64_call.result.res)
    expected_output = Data.from_hex(example_addr).to_ints().values

    assert output == expected_output
