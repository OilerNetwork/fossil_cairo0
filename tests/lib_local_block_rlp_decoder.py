import pytest
from utils.block_header import build_block_header
from utils.benchmarks.blockheader_rlp_extractor import getBaseFee, getBeneficiary, getParentHash, getOmmersHash, getStateRoot, getBlocknumber, getDifficulty, getTransactionsRoot, getReceiptsRoot, getGasLimit, getGasUsed, getTimestamp
from mocks.blocks import mocked_blocks
from utils.types import Data


@pytest.mark.asyncio
async def test_decode_parent_hash():
    # Retrieve rlp block header
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()

    assert block_header.hash() == block["hash"]
    block_rlp_formatted = Data.from_bytes(block_rlp).to_ints()

    extracted_hash = Data.from_ints(getParentHash(block_rlp_formatted)).to_bytes()

    assert block["parentHash"] == extracted_hash

@pytest.mark.asyncio
async def test_decode_uncles_hash():
    # Retrieve rlp block header
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()

    assert block_header.hash() == block["hash"]
    block_rlp_formatted = Data.from_bytes(block_rlp).to_ints()

    extracted_hash = Data.from_ints(getOmmersHash(block_rlp_formatted)).to_bytes()

    assert block["sha3Uncles"] == extracted_hash

@pytest.mark.asyncio
async def test_decode_beneficiary():
    # Retrieve rlp block header
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()

    assert block_header.hash() == block["hash"]
    block_rlp_formatted = Data.from_bytes(block_rlp).to_ints()

    extracted_hash = Data.from_ints(getBeneficiary(block_rlp_formatted)).to_bytes()

    assert bytes.fromhex(block["miner"][2:]) == extracted_hash

@pytest.mark.asyncio
async def test_decode_state_root():
    # Retrieve rlp block header
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()

    assert block_header.hash() == block["hash"]
    block_rlp_formatted = Data.from_bytes(block_rlp).to_ints()

    extracted_hash = Data.from_ints(getStateRoot(block_rlp_formatted)).to_bytes()

    assert block["stateRoot"] == extracted_hash

@pytest.mark.asyncio
async def test_decode_transactions_root():
    # Retrieve rlp block header
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()

    assert block_header.hash() == block["hash"]
    block_rlp_formatted = Data.from_bytes(block_rlp).to_ints()

    extracted_hash = Data.from_ints(getTransactionsRoot(block_rlp_formatted)).to_bytes()

    assert block["transactionsRoot"] == extracted_hash

@pytest.mark.asyncio
async def test_decode_receipts_root():
    # Retrieve rlp block header
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()

    assert block_header.hash() == block["hash"]
    block_rlp_formatted = Data.from_bytes(block_rlp).to_ints()

    extracted_hash = Data.from_ints(getReceiptsRoot(block_rlp_formatted)).to_bytes()

    assert block["receiptsRoot"] == extracted_hash

@pytest.mark.asyncio
async def test_decode_difficulty():
    # Retrieve rlp block header
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()

    assert block_header.hash() == block["hash"]
    block_rlp_formatted = Data.from_bytes(block_rlp).to_ints()

    difficulty = Data.from_ints(getDifficulty(block_rlp_formatted))

    assert block["difficulty"] == difficulty.to_int()

@pytest.mark.asyncio
async def test_decode_block_number():
    # Retrieve rlp block header
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()

    assert block_header.hash() == block["hash"]
    block_rlp_formatted = Data.from_bytes(block_rlp).to_ints()

    block_number = Data.from_ints(getBlocknumber(block_rlp_formatted))

    assert block["number"] == block_number.to_int()


@pytest.mark.asyncio
async def test_decode_gasLimit():
    # Retrieve rlp block header
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()

    assert block_header.hash() == block["hash"]
    block_rlp_formatted = Data.from_bytes(block_rlp).to_ints()

    gasLimit = Data.from_ints(getGasLimit(block_rlp_formatted))

    assert block["gasLimit"] == gasLimit.to_int()


@pytest.mark.asyncio
async def test_decode_getGasUsed():
    # Retrieve rlp block header
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()

    assert block_header.hash() == block["hash"]
    block_rlp_formatted = Data.from_bytes(block_rlp).to_ints()

    gasUsed = Data.from_ints(getGasUsed(block_rlp_formatted))

    assert block["gasUsed"] == gasUsed.to_int()



@pytest.mark.asyncio
async def test_decode_getTimestamp():
    # Retrieve rlp block header
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()

    assert block_header.hash() == block["hash"]
    block_rlp_formatted = Data.from_bytes(block_rlp).to_ints()

    timestamp = Data.from_ints(getTimestamp(block_rlp_formatted))

    assert block["timestamp"] == timestamp.to_int()


@pytest.mark.asyncio
async def test_decode_getBaseFee():
    # Retrieve rlp block header
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()

    assert block_header.hash() == block["hash"]
    block_rlp_formatted = Data.from_bytes(block_rlp).to_ints()

    baseFee = Data.from_ints(getBaseFee(block_rlp_formatted))

    assert block["baseFeePerGas"] == baseFee.to_int()