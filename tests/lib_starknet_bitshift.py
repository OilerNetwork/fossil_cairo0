import pytest
from typing import NamedTuple
from random import randint
from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.testing.starknet import Starknet

from utils.helpers import random_bytes, bytes_to_int


bytes_to_int_big = lambda word: bytes_to_int(word)

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
async def test_bitshift_right():
    starknet, bitshift_contract = await setup()

    input_bytes = random_bytes(8)
    input = bytes_to_int_big(input_bytes)

    bits_shifted = randint(0, 64)

    right_bitshift_call = await bitshift_contract.test_bitshift_right(input, bits_shifted).call()
    assert input >> bits_shifted == right_bitshift_call.result.shifted


@pytest.mark.asyncio
async def test_bitshift_left():
    starknet, bitshift_contract = await setup()

    input_bytes = random_bytes(8)
    input = bytes_to_int_big(input_bytes)

    bits_shifted = randint(0, 64)

    left_bitshift_call = await bitshift_contract.test_bitshift_left(input, bits_shifted).call()

    expected = (input << bits_shifted) & (2**64 - 1)
    assert expected == left_bitshift_call.result.shifted