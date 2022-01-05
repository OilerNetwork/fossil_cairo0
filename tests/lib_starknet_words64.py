import asyncio
import pytest
from typing import NamedTuple

from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.testing.starknet import Starknet
from starkware.starkware_utils.error_handling import StarkException

from utils.types import Data
from utils.helpers import random_bytes

class TestsDeps(NamedTuple):
    starknet: Starknet
    words64: StarknetContract

@pytest.fixture(scope='module')
def event_loop():
    return asyncio.new_event_loop()

async def setup():
    starknet = await Starknet.empty()
    words64 = await starknet.deploy(source="contracts/starknet/test/TestWords64.cairo", cairo_path=["contracts"])
    return TestsDeps(
        starknet=starknet,
        words64=words64
    )

@pytest.fixture(scope='module')
async def factory():
    return await setup()

@pytest.mark.asyncio
async def test_extract_nibble_from_single_word(factory):
    starknet, words64 = factory

    for word_length in range(1,9):
        input = Data.from_bytes(random_bytes(word_length))
        word = input.to_ints().values[0]
        for i in range(0, word_length*2):
            # print(f"extracting {i} nibble from {len(input.to_bytes())} bytes word")
            extract_nibble_call = await words64.test_extract_nibble(word, len(input.to_bytes()), i).call()
            res = extract_nibble_call.result.res
            expected_res = input.to_nibbles()[i]
            assert res == expected_res, f"Expected {res} to be equal {expected_res} for extracted position {i}"

@pytest.mark.asyncio
async def test_extract_nibble_from_ints_sequence(factory):
    starknet, words64 = factory

    for word_length in range(1,35):
        input = Data.from_bytes(random_bytes(word_length))
        for i in range(0, len(input.to_bytes())*2):
            extract_nibble_call = await words64.test_extract_nibble_from_words(input.to_ints().values, input.to_ints().length, i).call()
            res = extract_nibble_call.result.res
            expected_res = input.to_nibbles()[i]
            assert res == expected_res, f"Expected {res} to be equal {expected_res} for extracted position {i}"

@pytest.mark.asyncio
async def test_extract_nibble_invalid_position(factory):
    starknet, words64 = factory

    input = Data.from_bytes(random_bytes(29))
    word = input.to_ints().values[0]

    with pytest.raises(StarkException):
        await words64.test_extract_nibble(word, len(input.to_bytes()), 16).call()