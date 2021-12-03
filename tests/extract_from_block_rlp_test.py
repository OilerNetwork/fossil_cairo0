from typing import List, NamedTuple
import pytest

from utils.helpers import chunk_bytes_input, bytes_to_int_big, ints_array_to_bytes, random_bytes, print_ints_array
from utils.block_header import build_block_header
from utils.benchmarks.extract_from_block_rlp import extractData
from mocks.blocks import mocked_blocks

@pytest.mark.asyncio
async def test_random():
    block_rlp = random_bytes(1337)
    # print("\n0x" + block_rlp.hex())

    block_rlp_chunked = chunk_bytes_input(block_rlp)
    block_rlp_formatted = list(map(bytes_to_int_big, block_rlp_chunked))

    for start_byte in range(0, 1200):
        for size in range(1, 66):
            # print("start_byte:", start_byte, "size:", size)
            extracted_words = extractData(block_rlp_formatted, start_byte, size)
            # print(print_ints_array(extracted_words))
            extracted_bytes = ints_array_to_bytes(extracted_words, size)
            expected_bytes = block_rlp[start_byte:start_byte+size]
            assert extracted_bytes == expected_bytes

    # print("\nPython: " , "0x" + expected_hash.hex())
    # print(" Block: ", block["parentHash"].hex())

    # assert block["parentHash"] == expected_hash

# @pytest.mark.asyncio
# async def test_int_to_bytes():
#     expected_bytes_array = b'\xf9\x02\x18\xa0\x03\xb0\x16\xcc\x93\x87\xcb\x3c\xef\x86\xd9\xd4\xaf\xb5\x2c\x37\x89\x52\x8c\x53\x0c\x00\x20\x87\x95\xac\x93\x7c\x00\x77'

#     bytes_array_chunked = chunk_bytes_input(expected_bytes_array)
#     ints_array = list(map(bytes_to_int_big, bytes_array_chunked))

#     output_bytes_array = ints_array_to_bytes(ints_array, len(expected_bytes_array))

#     print("\n")
#     print(expected_bytes_array.hex())
#     print(output_bytes_array.hex())

#     assert expected_bytes_array == output_bytes_array
