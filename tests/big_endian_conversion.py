from typing import NamedTuple
import pytest
from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.testing.starknet import Starknet

from utils.helpers import string_to_byte


class TestsDeps(NamedTuple):
    starknet: Starknet
    converter: StarknetContract


async def setup():
    starknet = await Starknet.empty()
    converter = await starknet.deploy("contracts/starknet/test/TestToBigEndian.cairo", cairo_path=["contracts"])
    return TestsDeps(starknet=starknet, converter=converter)

@pytest.mark.asyncio
async def test_to_big_endian():
    starknet, converter = await setup()

    input_str = 'f90218a0'
    little_endian_input = string_to_byte(input_str)

    convert_call = await converter.test_to_big_endian(little_endian_input).call()
    output = convert_call.result.res

    assert output == int.from_bytes(input_str.encode("UTF-8"), 'big')

