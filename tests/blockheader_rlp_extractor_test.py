import pytest
from utils.helpers import chunk_bytes_input, bytes_to_int_big, ints_array_to_bytes
from utils.block_header import build_block_header
from utils.benchmarks.blockheader_rlp_extractor import getParentHash, getOmmersHash, getStateRoot, getBlockNumber
from mocks.blocks import mocked_blocks

@pytest.mark.asyncio
async def test_decode_parent_hash():
    # Retrieve rlp block header
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()

    assert block_header.hash() == block["hash"]
    block_rlp_chunked = chunk_bytes_input(block_rlp)
    block_rlp_formatted = list(map(bytes_to_int_big, block_rlp_chunked))

    extracted_hash = ints_array_to_bytes(getParentHash(block_rlp_formatted), 32)

    assert block["parentHash"] == extracted_hash

@pytest.mark.asyncio
async def test_decode_uncles_hash():
    # Retrieve rlp block header
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()

    assert block_header.hash() == block["hash"]
    block_rlp_chunked = chunk_bytes_input(block_rlp)
    block_rlp_formatted = list(map(bytes_to_int_big, block_rlp_chunked))

    extracted_hash = ints_array_to_bytes(getOmmersHash(block_rlp_formatted), 32)

    assert block["sha3Uncles"] == extracted_hash

@pytest.mark.asyncio
async def test_decode_state_root():
    # Retrieve rlp block header
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()

    assert block_header.hash() == block["hash"]
    block_rlp_chunked = chunk_bytes_input(block_rlp)
    block_rlp_formatted = list(map(bytes_to_int_big, block_rlp_chunked))

    extracted_hash = ints_array_to_bytes(getStateRoot(block_rlp_formatted), 32)

    assert block["stateRoot"] == extracted_hash

@pytest.mark.asyncio
async def test_decode_block_number():
    # Retrieve rlp block header
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()

    assert block_header.hash() == block["hash"]
    block_rlp_chunked = chunk_bytes_input(block_rlp)
    block_rlp_formatted = list(map(bytes_to_int_big, block_rlp_chunked))

    block_number = getBlockNumber(block_rlp_formatted)

    assert block["number"] == block_number