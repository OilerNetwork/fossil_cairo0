import pytest
import asyncio
from typing import Tuple, NamedTuple
from random import randint
from utils.helpers import IntsSequence, split_uint256_to_uint, uint_to_ints_array
from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.testing.starknet import Starknet

class TestsDeps(NamedTuple):
    starknet: Starknet
    ints_to_uint256: StarknetContract

@pytest.fixture(scope='module')
def event_loop():
    return asyncio.new_event_loop()

async def setup():
    starknet = await Starknet.empty()
    ints_to_uint256 = await starknet.deploy(source="contracts/starknet/test/TestIntsToUint256.cairo", cairo_path=["contracts"])
    return TestsDeps(
        starknet=starknet,
        ints_to_uint256=ints_to_uint256
    )

@pytest.fixture(scope='module')
async def factory():
    return await setup()

@pytest.mark.asyncio 
async def test_covert_0(factory):
    starknet, ints_to_uint256 = factory 
    num = 0
    ints = uint_to_ints_array(num)
    ints_to_uint256_call = await ints_to_uint256.test_ints_to_uint256(ints.length,ints.values).call()
    assert split_uint256_to_uint(ints_to_uint256_call.result.uint256) == num

@pytest.mark.asyncio 
async def test_covert_1(factory):
    starknet, ints_to_uint256 = factory 
    num = 1
    ints = uint_to_ints_array(num)
    ints_to_uint256_call = await ints_to_uint256.test_ints_to_uint256(ints.length,ints.values).call()
    assert split_uint256_to_uint(ints_to_uint256_call.result.uint256) == num

@pytest.mark.asyncio 
async def test_covert_random(factory):
    starknet, ints_to_uint256 = factory 
    num = randint(0, (2**256) - 1)
    ints = uint_to_ints_array(num)
    ints_to_uint256_call = await ints_to_uint256.test_ints_to_uint256(ints.length,ints.values).call()
    assert split_uint256_to_uint(ints_to_uint256_call.result.uint256) == num

@pytest.mark.asyncio 
async def test_covert_out_of_bound(factory):
    starknet, ints_to_uint256 = factory 
    num = randint(2**256, 2**512) 
    ints = uint_to_ints_array(num)
    with pytest.raises(Exception):
        await ints_to_uint256.test_ints_to_uint256(ints.length,ints.values).call()
