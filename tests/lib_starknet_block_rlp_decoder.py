from typing import List, NamedTuple
import pytest
from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.testing.starknet import Starknet

from utils.helpers import chunk_bytes_input, bytes_to_int
from utils.block_header import build_block_header
from utils.benchmarks.blockheader_rlp_extractor import (
    getParentHash,
    getOmmersHash,
    getBeneficiary,
    getStateRoot,
    getTransactionsRoot,
    getReceiptsRoot,
    getDifficulty,
    getBlocknumber
)
from mocks.blocks import mocked_blocks
from utils.types import Data


bytes_to_int_big = lambda word: bytes_to_int(word)


class TestsDeps(NamedTuple):
    starknet: Starknet
    decoder: StarknetContract


async def setup():
    starknet = await Starknet.empty()
    decoder = await starknet.deploy("contracts/starknet/test/TestRlpDecoder.cairo", cairo_path=["contracts"])
    return TestsDeps(starknet=starknet, decoder=decoder)


@pytest.mark.asyncio
async def test_decode_parent_hash():
    starknet, decoder = await setup()

    # Retrieve rlp block header
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()

    assert block_header.hash() == block["hash"]
    block_rlp_chunked = chunk_bytes_input(block_rlp)
    block_rlp_formatted = list(map(bytes_to_int_big, block_rlp_chunked))

    decoded = await decoder.test_decode_parent_hash(block_rlp_formatted).call()
    output = '0x' + ''.join(v.to_bytes(8, 'big').hex() for v in decoded.result.res)

    expected_words = getParentHash(block_rlp_formatted)
    expected_hash = Data.from_ints(expected_words).to_hex()
    assert output == expected_hash

@pytest.mark.asyncio
async def test_decode_uncles_hash():
    starknet, decoder = await setup()

    # Retrieve rlp block header
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()

    assert block_header.hash() == block["hash"]
    block_rlp_chunked = chunk_bytes_input(block_rlp)
    block_rlp_formatted = list(map(bytes_to_int_big, block_rlp_chunked))

    decoded = await decoder.test_decode_uncles_hash(block_rlp_formatted).call()
    output = '0x' + ''.join(v.to_bytes(8, 'big').hex() for v in decoded.result.res)

    expected_words = getOmmersHash(block_rlp_formatted)
    expected_hash = Data.from_ints(expected_words).to_hex()
    assert output == expected_hash

@pytest.mark.asyncio
async def test_decode_beneficiary():
    starknet, decoder = await setup()

    # Retrieve rlp block header
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()

    assert block_header.hash() == block["hash"]
    block_rlp_chunked = chunk_bytes_input(block_rlp)
    block_rlp_formatted = list(map(bytes_to_int_big, block_rlp_chunked))

    decoded = await decoder.test_decode_beneficiary(block_rlp_formatted).call()
    output_words = list(decoded.result.res)

    expected_words = getBeneficiary(block_rlp_formatted)

    assert output_words == expected_words.values

@pytest.mark.asyncio
async def test_decode_state_root():
    starknet, decoder = await setup()

    # Retrieve rlp block header
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()

    assert block_header.hash() == block["hash"]
    block_rlp_chunked = chunk_bytes_input(block_rlp)
    block_rlp_formatted = list(map(bytes_to_int_big, block_rlp_chunked))

    decoded = await decoder.test_decode_state_root(block_rlp_formatted).call()
    output = '0x' + ''.join(v.to_bytes(8, 'big').hex() for v in decoded.result.res)

    expected_words = getStateRoot(block_rlp_formatted)
    expected_hash = Data.from_ints(expected_words).to_hex()
    assert output == expected_hash

@pytest.mark.asyncio
async def test_decode_transactions_root():
    starknet, decoder = await setup()

    # Retrieve rlp block header
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()

    assert block_header.hash() == block["hash"]
    block_rlp_chunked = chunk_bytes_input(block_rlp)
    block_rlp_formatted = list(map(bytes_to_int_big, block_rlp_chunked))

    decoded = await decoder.test_decode_transactions_root(block_rlp_formatted).call()
    output = '0x' + ''.join(v.to_bytes(8, 'big').hex() for v in decoded.result.res)

    expected_words = getTransactionsRoot(block_rlp_formatted)
    expected_hash = Data.from_ints(expected_words).to_hex()
    assert output == expected_hash

@pytest.mark.asyncio
async def test_decode_transactions_root():
    starknet, decoder = await setup()

    # Retrieve rlp block header
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()

    assert block_header.hash() == block["hash"]
    block_rlp_chunked = chunk_bytes_input(block_rlp)
    block_rlp_formatted = list(map(bytes_to_int_big, block_rlp_chunked))

    decoded = await decoder.test_decode_transactions_root(block_rlp_formatted).call()
    output = '0x' + ''.join(v.to_bytes(8, 'big').hex() for v in decoded.result.res)

    expected_words = getTransactionsRoot(block_rlp_formatted)
    expected_hash = Data.from_ints(expected_words).to_hex()
    assert output == expected_hash

@pytest.mark.asyncio
async def test_decode_receipts_root():
    starknet, decoder = await setup()

    # Retrieve rlp block header
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()

    assert block_header.hash() == block["hash"]
    block_rlp_chunked = chunk_bytes_input(block_rlp)
    block_rlp_formatted = list(map(bytes_to_int_big, block_rlp_chunked))

    decoded = await decoder.test_decode_receipts_root(block_rlp_formatted).call()
    output = '0x' + ''.join(v.to_bytes(8, 'big').hex() for v in decoded.result.res)

    expected_words = getReceiptsRoot(block_rlp_formatted)
    expected_hash = Data.from_ints(expected_words).to_hex()
    assert output == expected_hash

@pytest.mark.asyncio
async def test_decode_difficulty():
    starknet, decoder = await setup()

    # Retrieve rlp block header
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()

    assert block_header.hash() == block["hash"]
    block_rlp_chunked = chunk_bytes_input(block_rlp)
    block_rlp_formatted = list(map(bytes_to_int_big, block_rlp_chunked))

    decoded = await decoder.test_decode_difficulty(block_rlp_formatted).call()

    output = decoded.result.res
    expected_value = getDifficulty(block_rlp_formatted)
    assert output == expected_value

@pytest.mark.asyncio
async def test_decode_block_number():
    starknet, decoder = await setup()

    # Retrieve rlp block header
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()

    assert block_header.hash() == block["hash"]
    block_rlp_chunked = chunk_bytes_input(block_rlp)
    block_rlp_formatted = list(map(bytes_to_int_big, block_rlp_chunked))

    decoded = await decoder.test_decode_block_number(block_rlp_formatted).call()

    output = decoded.result.res
    expected_value = getBlocknumber(block_rlp_formatted)
    assert output == expected_value
