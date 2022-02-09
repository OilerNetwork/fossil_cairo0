import pytest
import asyncio
from typing import NamedTuple
from random import randint

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
async def test_bitset(factory):
    starknet, bitset_contract = factory

    for i in range(0, 16):
        bitset = 2**i
        get_bitset_position_call = await bitset_contract.test_bitset_get(bitset, i).call()
        assert get_bitset_position_call.result.res == 1

@pytest.mark.asyncio
async def test_bitset_random(factory):
    starknet, bitset_contract = factory

    for i in range(0, 10):
        bitset = randint(0, 2**16-1)
        sum = 0
        for bit in range(0, 16):
            get_bitset_position_call = await bitset_contract.test_bitset_get(bitset, bit).call()
            sum += get_bitset_position_call.result.res * 2**bit
        assert sum == bitset

@pytest.mark.asyncio
async def test_bitset_all_zeroes(factory):
    starknet, bitset_contract = factory

    bitset = 0
    for bit in range(0, 16):
        get_bitset_position_call = await bitset_contract.test_bitset_get(bitset, bit).call()
        assert get_bitset_position_call.result.res == 0

@pytest.mark.asyncio
async def test_bitset_all_ones(factory):
    starknet, bitset_contract = factory

    bitset = 2**16 - 1
    for bit in range(0, 16):
        get_bitset_position_call = await bitset_contract.test_bitset_get(bitset, bit).call()
        assert get_bitset_position_call.result.res == 1
