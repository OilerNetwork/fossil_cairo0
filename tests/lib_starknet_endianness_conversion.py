import pytest
import asyncio
from typing import NamedTuple
from utils.types import Data
from utils.helpers import IntsSequence

from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.testing.starknet import Starknet

class TestsDeps(NamedTuple):
    starknet: Starknet
    converter: StarknetContract

@pytest.fixture(scope='module')
def event_loop():
    return asyncio.new_event_loop()

async def setup():
    starknet = await Starknet.empty()
    converter = await starknet.deploy("contracts/starknet/test/TestToBigEndian.cairo", cairo_path=["contracts"])
    return TestsDeps(starknet=starknet, converter=converter)

@pytest.fixture(scope='module')
async def factory():
    return await setup()


def byteswap_64bit_word(word: int, size: int):
    swapped_bytes = ((word & 0xFF00FF00FF00FF00) >> 8) | ((word & 0x00FF00FF00FF00FF) << 8)
    swapped_2byte_pair = ((swapped_bytes & 0xFFFF0000FFFF0000) >> 16) | ((swapped_bytes & 0x0000FFFF0000FFFF) << 16)
    swapped_4byte_pair = (swapped_2byte_pair >> 32) | ((swapped_2byte_pair << 32) % 2**64)

    # Some Shiva-inspired code here
    if (size == 8):
        return swapped_4byte_pair
    else:
        return swapped_4byte_pair >> ((8-size)*8)

@pytest.mark.asyncio
async def test_swap_endianness_full_word(factory):
    starknet, converter = factory

    input_str = 'f90218a089abcdef'

    input_as_big_endian = int.from_bytes(bytearray.fromhex(input_str), 'big')

    input_as_little_endian = int.from_bytes(bytearray.fromhex(input_str), 'little')

    big_to_little_python = byteswap_64bit_word(input_as_big_endian, int(len(input_str)/2))

    assert big_to_little_python == input_as_little_endian

    convert_call = await converter.test_to_big_endian(input_as_big_endian, int(len(input_str)/2)).call()
    big_to_little_cairo = convert_call.result.res

    assert big_to_little_python == big_to_little_cairo

    little_to_big_python = byteswap_64bit_word(input_as_little_endian, int(len(input_str)/2))

    assert little_to_big_python == input_as_big_endian

    convert_call = await converter.test_to_big_endian(input_as_little_endian, int(len(input_str)/2)).call()
    little_to_big_cairo = convert_call.result.res


    assert little_to_big_python == little_to_big_cairo


@pytest.mark.asyncio
async def test_swap_endianness_small_words(factory):
    starknet, converter = factory
    for i in range(8):
        input_str = 'f90218a089abcdef'[0:16-(i*2)]
        input_as_big_endian = int.from_bytes(bytearray.fromhex(input_str), 'big')
        input_as_little_endian = int.from_bytes(bytearray.fromhex(input_str), 'little')
        big_to_little_python = byteswap_64bit_word(input_as_big_endian, int(len(input_str)/2))
        assert big_to_little_python == input_as_little_endian
        convert_call = await converter.test_to_big_endian(input_as_big_endian, int(len(input_str)/2)).call()
        big_to_little_cairo = convert_call.result.res
        assert big_to_little_python == big_to_little_cairo

@pytest.mark.asyncio
async def test_swap_endianness_small_word(factory):
    starknet, converter = factory

    input_str = 'f90218'

    input_as_big_endian = int.from_bytes(bytearray.fromhex(input_str), 'big')

    input_as_little_endian = int.from_bytes(bytearray.fromhex(input_str), 'little')

    big_to_little_python = byteswap_64bit_word(input_as_big_endian, int(len(input_str)/2))

    assert big_to_little_python == input_as_little_endian

    convert_call = await converter.test_to_big_endian(input_as_big_endian, int(len(input_str)/2)).call()
    big_to_little_cairo = convert_call.result.res

    assert big_to_little_python == big_to_little_cairo

    little_to_big_python = byteswap_64bit_word(input_as_little_endian, int(len(input_str)/2))

    assert little_to_big_python == input_as_big_endian

    convert_call = await converter.test_to_big_endian(input_as_little_endian, int(len(input_str)/2)).call()
    little_to_big_cairo = convert_call.result.res

    assert little_to_big_python == little_to_big_cairo

@pytest.mark.asyncio
async def test_to_little_endian(factory):
    starknet, converter = factory

    input_str = 'f90218'#a089abcdef'

    big_endian_input = int.from_bytes(bytearray.fromhex(input_str), 'big')

    little_swapped = byteswap_64bit_word(big_endian_input, int(len(input_str)/2))

    convert_call = await converter.test_to_big_endian(big_endian_input, int(len(input_str)/2)).call()
    output = convert_call.result.res

    assert output == little_swapped

@pytest.mark.asyncio
async def test_tricky_case(factory):
    starknet, converter = factory

    input_str = '0000f9'

    big_endian_input = int.from_bytes(bytearray.fromhex(input_str), 'big')

    little_swapped = byteswap_64bit_word(big_endian_input, int(len(input_str)/2))

    convert_call = await converter.test_to_big_endian(big_endian_input, int(len(input_str)/2)).call()
    output = convert_call.result.res

    assert output == little_swapped

@pytest.mark.asyncio
async def test_revert_word_size_above_64bit(factory):
    starknet, converter = factory
    with pytest.raises(Exception):
        max_word = 2 ** 64 + 1
        await converter.test_to_big_endian(max_word, int(len("dedd")/2)).call()

@pytest.mark.asyncio
async def test_swap_endianness_many_words(factory):
    starknet, converter = factory

    input = Data.from_hex('0x881e56a54ebf4520546331bcafd9d0a41a967eac92e89fe4521156b9f4f1685e')

    convert_call = await converter.test_four_words_to_big_endian(input.to_ints().values, input.to_ints().length).call()
    output = Data.from_ints(IntsSequence(convert_call.result.res, convert_call.result.res_len_bytes))

    expected_output = Data.from_hex('0x2045bf4ea5561e88a4d0d9afbc316354e49fe892ac7e961a5e68f1f4b9561152')

    assert output == expected_output