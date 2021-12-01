from typing import List, NamedTuple
import pytest

from utils.helpers import chunk_bytes_input, bytes_to_int_big, ints_array_to_bytes, random_bytes, print_ints_array
from utils.block_header import build_block_header
from utils.benchmarks.extract_from_block_rlp import extract_from_block_rlp, getBlockNumberPosition, extract_element
from mocks.blocks import mocked_blocks

@pytest.mark.asyncio
async def test_decode_parent_hash():
    # Retrieve rlp block header
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()

    print(block_rlp.hex()[:90])

    print("RLP lenght:", len(block_rlp))

    assert block_header.hash() == block["hash"]
    block_rlp_chunked = chunk_bytes_input(block_rlp)
    block_rlp_formatted = list(map(bytes_to_int_big, block_rlp_chunked))

    # "rlp length" length = 1 byte ("f9" means "f7"+2)
    #          rlp length = usually 2 bytes if the above is "f9"
    #   parentHash length = 1 byte (should be)
    parentHash_position = 1+2+1 

    extracted_words = extract_from_block_rlp(block_rlp_formatted, parentHash_position, 32)
    extracted_hash = ints_array_to_bytes(extracted_words, 32)

    print("\nPython: " , "0x" + extracted_hash.hex())
    print(" Block: ", block["parentHash"].hex())

    assert block["parentHash"] == extracted_hash

@pytest.mark.asyncio
async def test_decode_uncles_hash():
    # Retrieve rlp block header
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()

    print(block_rlp.hex()[:90])

    print("RLP lenght:", len(block_rlp))

    assert block_header.hash() == block["hash"]
    block_rlp_chunked = chunk_bytes_input(block_rlp)
    block_rlp_formatted = list(map(bytes_to_int_big, block_rlp_chunked))

    # "rlp length" length = 1 byte ("f9" means "f7"+2)
    #          rlp length = usually 2 bytes if the above is "f9"
    #   parentHash length = 1 byte (should be)
    #          parentHash = 32 bytes (should be)
    #   unclesHash length = 1 byte (should be)
    unclesHash_position = 1+2+1+32+1

    extracted_words = extract_from_block_rlp(block_rlp_formatted, unclesHash_position, 32)
    extracted_hash = ints_array_to_bytes(extracted_words, 32)

    print("\nPython: " , "0x" + extracted_hash.hex())
    print(" Block: ", block["sha3Uncles"].hex())

    assert block["sha3Uncles"] == extracted_hash

@pytest.mark.asyncio
async def test_decode_state_root():
    # Retrieve rlp block header
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()

    print(block_rlp.hex()[:90])

    print("RLP lenght:", len(block_rlp))

    assert block_header.hash() == block["hash"]
    block_rlp_chunked = chunk_bytes_input(block_rlp)
    block_rlp_formatted = list(map(bytes_to_int_big, block_rlp_chunked))

    # "rlp length" length = 1 byte ("f9" means "f7"+2)
    #          rlp length = usually 2 bytes if the above is "f9"
    #   parentHash length = 1 byte (should be)
    #          parentHash = 32 bytes (should be)
    #   unclesHash length = 1 byte (should be)
    #          unclesHash = 32 bytes (should be)
    #  beneficiary length = 1 byte (should be)
    #         beneficiary = 20 bytes (should be)
    #    stateRoot length = 1 byte (should be)

    unclesHash_position = 1+2+1+32+1+32+1+20+1

    extracted_words = extract_from_block_rlp(block_rlp_formatted, unclesHash_position, 32)
    extracted_hash = ints_array_to_bytes(extracted_words, 32)

    print("\nPython: " , "0x" + extracted_hash.hex())
    print(" Block: ", block["stateRoot"].hex())

    assert block["stateRoot"] == extracted_hash

@pytest.mark.asyncio
async def test_decode_block_number():
    # Retrieve rlp block header
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()

    print(block_rlp.hex()[:90])

    print("RLP lenght:", len(block_rlp))

    assert block_header.hash() == block["hash"]
    block_rlp_chunked = chunk_bytes_input(block_rlp)
    block_rlp_formatted = list(map(bytes_to_int_big, block_rlp_chunked))

    block_number_position = getBlockNumberPosition(block_rlp_formatted)
    print("block_number_position:", block_number_position)

    print("block number part:", block_rlp[block_number_position:block_number_position+10].hex())

    block_number_bytes = extract_element(block_rlp_formatted, block_number_position)
    block_number = int.from_bytes(block_number_bytes, "big")

    print("\nPython: " , "0x" + block_number_bytes.hex())
    print(" Block number: ", block["number"], hex(block["number"]))

    assert block["number"] == block_number

# @pytest.mark.asyncio
# async def test_random():
#     block_rlp = random_bytes(1337)
#     # print("\n0x" + block_rlp.hex())

#     block_rlp_chunked = chunk_bytes_input(block_rlp)
#     block_rlp_formatted = list(map(bytes_to_int_big, block_rlp_chunked))

#     for start_byte in range(0, 1200):
#         for size in range(1, 66):
#             # print("start_byte:", start_byte, "size:", size)
#             extracted_words = extract_from_block_rlp(block_rlp_formatted, start_byte, size)
#             # print(print_ints_array(extracted_words))
#             extracted_bytes = ints_array_to_bytes(extracted_words, size)
#             expected_bytes = block_rlp[start_byte:start_byte+size]
#             assert extracted_bytes == expected_bytes

#     # print("\nPython: " , "0x" + expected_hash.hex())
#     # print(" Block: ", block["parentHash"].hex())

#     # assert block["parentHash"] == expected_hash

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
