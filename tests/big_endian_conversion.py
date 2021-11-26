from typing import NamedTuple
import pytest
from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.testing.starknet import Starknet

from utils.helpers import string_to_byte


class TestsDeps(NamedTuple):
    starknet: Starknet
    converter: StarknetContract


def byteswap_64bit_word(word: int):
    swapped_bytes = ((word & 0xFF00FF00FF00FF00) >> 8) | ((word & 0x00FF00FF00FF00FF) << 8)
    swapped_2byte_pair = ((swapped_bytes & 0xFFFF0000FFFF0000) >> 16) | ((swapped_bytes & 0x0000FFFF0000FFFF) << 16)
    swapped_4byte_pair = (swapped_2byte_pair >> 32) | ((swapped_2byte_pair << 32) % 2**64)
    return swapped_4byte_pair


async def setup():
    starknet = await Starknet.empty()
    converter = await starknet.deploy("contracts/starknet/test/TestToBigEndian.cairo", cairo_path=["contracts"])
    return TestsDeps(starknet=starknet, converter=converter)

@pytest.mark.asyncio
async def test_to_big_endian():
    starknet, converter = await setup()

    input_str = 'f90218a089abcdef'

    print(bin(int(input_str, 16)))

    big_endian_input = int.from_bytes(input_str.encode("UTF-8"), 'big')
    little_endian_input = string_to_byte(input_str)

    print('\n')

    swapped = byteswap_64bit_word(int(input_str, 16))
    swapped_hex = hex(swapped)[2:]

    print(swapped_hex)

    print("Vanilla python: ", int.from_bytes(bytes.fromhex(swapped_hex), 'little'))

    print("Big: ", (big_endian_input))
    print("Lit: ", (little_endian_input))

    # convert_call = await converter.test_to_big_endian(little_endian_input).call()
    # output = convert_call.result.res

    # assert output == int.from_bytes(input_str.encode("UTF-8"), 'big')

@pytest.mark.asyncio
async def test_revert_word_size_above_64bit():
    starknet, converter = await setup()
    with pytest.raises(Exception):
        max_word = 9223372036854775807 + 1
        await converter.test_to_big_endian(max_word).call()
