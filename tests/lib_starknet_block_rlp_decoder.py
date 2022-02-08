import pytest
import asyncio
from typing import  NamedTuple
from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.testing.starknet import Starknet

from utils.helpers import IntsSequence
from utils.block_header import build_block_header
from utils.benchmarks.blockheader_rlp_extractor import (
    getParentHash,
    getOmmersHash,
    getBeneficiary,
    getStateRoot,
    getTransactionsRoot,
    getReceiptsRoot,
    getDifficulty,
    getBlocknumber,
    getGasLimit,
    getGasUsed,
    getTimestamp,
    getBaseFee
)
from mocks.blocks import mocked_blocks
from utils.types import Data


class TestsDeps(NamedTuple):
    starknet: Starknet
    decoder: StarknetContract


@pytest.fixture(scope='module')
def event_loop():
    return asyncio.new_event_loop()

async def setup():
    starknet = await Starknet.empty()
    decoder = await starknet.deploy("contracts/starknet/test/TestRlpDecoder.cairo", cairo_path=["contracts"])
    return TestsDeps(starknet=starknet, decoder=decoder)

@pytest.fixture(scope='module')
async def factory():
    return await setup()


@pytest.mark.asyncio
async def test_decode_parent_hash(factory):
    starknet, decoder = factory

    # Retrieve rlp block header
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = Data.from_bytes(block_header.raw_rlp()).to_ints()

    assert block_header.hash() == block["hash"]

    call = await decoder.test_decode_parent_hash(block_rlp.length, block_rlp.values).call()
    output = Data.from_ints(IntsSequence(list(call.result.res), 32))

    expected_output = Data.from_ints(getParentHash(block_rlp))
    assert output == expected_output

@pytest.mark.asyncio
async def test_decode_uncles_hash(factory):
    starknet, decoder = factory

    # Retrieve rlp block header
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = Data.from_bytes(block_header.raw_rlp()).to_ints()

    assert block_header.hash() == block["hash"]

    call = await decoder.test_decode_uncles_hash(block_rlp.length, block_rlp.values).call()
    output = Data.from_ints(IntsSequence(list(call.result.res), 32))

    expected_output = Data.from_ints(getOmmersHash(block_rlp))
    assert output == expected_output

@pytest.mark.asyncio
async def test_decode_beneficiary(factory):
    starknet, decoder = factory

    # Retrieve rlp block header
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = Data.from_bytes(block_header.raw_rlp()).to_ints()

    assert block_header.hash() == block["hash"]

    call = await decoder.test_decode_beneficiary(block_rlp.length, block_rlp.values).call()
    output = Data.from_ints(IntsSequence(list(call.result.res), 20))

    expected_output = Data.from_ints(getBeneficiary(block_rlp))
    assert output == expected_output

@pytest.mark.asyncio
async def test_decode_state_root(factory):
    starknet, decoder = factory

    # Retrieve rlp block header
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = Data.from_bytes(block_header.raw_rlp()).to_ints()

    assert block_header.hash() == block["hash"]

    call = await decoder.test_decode_state_root(block_rlp.length, block_rlp.values).call()
    output = Data.from_ints(IntsSequence(list(call.result.res), 32))

    expected_output = Data.from_ints(getStateRoot(block_rlp))
    assert output == expected_output

@pytest.mark.asyncio
async def test_decode_transactions_root(factory):
    starknet, decoder = factory

    # Retrieve rlp block header
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = Data.from_bytes(block_header.raw_rlp()).to_ints()

    assert block_header.hash() == block["hash"]

    call = await decoder.test_decode_transactions_root(block_rlp.length, block_rlp.values).call()
    output = Data.from_ints(IntsSequence(list(call.result.res), 32))

    expected_output = Data.from_ints(getTransactionsRoot(block_rlp))
    assert output == expected_output

@pytest.mark.asyncio
async def test_decode_receipts_root(factory):
    starknet, decoder = factory

    # Retrieve rlp block header
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = Data.from_bytes(block_header.raw_rlp()).to_ints()

    assert block_header.hash() == block["hash"]

    call = await decoder.test_decode_receipts_root(block_rlp.length, block_rlp.values).call()
    output = Data.from_ints(IntsSequence(list(call.result.res), 32))

    expected_output = Data.from_ints(getReceiptsRoot(block_rlp))
    assert output == expected_output

@pytest.mark.asyncio
async def test_decode_difficulty(factory):
    starknet, decoder = factory

    # Retrieve rlp block header
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = Data.from_bytes(block_header.raw_rlp()).to_ints()

    assert block_header.hash() == block["hash"]

    call = await decoder.test_decode_difficulty(block_rlp.length, block_rlp.values).call()
    output = Data.from_int(call.result.res)

    expected_output = Data.from_ints(getDifficulty(block_rlp))
    assert output == expected_output

@pytest.mark.asyncio
async def test_decode_block_number(factory):
    starknet, decoder = factory

    # Retrieve rlp block header
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = Data.from_bytes(block_header.raw_rlp()).to_ints()

    assert block_header.hash() == block["hash"]

    call = await decoder.test_decode_block_number(block_rlp.length, block_rlp.values).call()
    output = Data.from_int(call.result.res)

    expected_output = Data.from_ints(getBlocknumber(block_rlp))
    assert output == expected_output

@pytest.mark.asyncio
async def test_decode_gas_limit(factory):
    starknet, decoder = factory

    # Retrieve rlp block header
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = Data.from_bytes(block_header.raw_rlp()).to_ints()

    assert block_header.hash() == block["hash"]

    call = await decoder.test_decode_gas_limit(block_rlp.length, block_rlp.values).call()
    output = Data.from_int(call.result.res)

    expected_output = Data.from_ints(getGasLimit(block_rlp))
    assert output == expected_output

@pytest.mark.asyncio
async def test_decode_gas_used(factory):
    starknet, decoder = factory

    for i in range(0, len(mocked_blocks)):
        block = mocked_blocks[i]
        block_header = build_block_header(block)
        block_rlp = Data.from_bytes(block_header.raw_rlp()).to_ints()

        assert block_header.hash() == block["hash"]

        call = await decoder.test_decode_gas_used(block_rlp.length, block_rlp.values).call()
        output = Data.from_int(call.result.res)

        expected_output = Data.from_ints(getGasUsed(block_rlp))
        assert output == expected_output

@pytest.mark.asyncio
async def test_decode_timestamp(factory):
    starknet, decoder = factory

    for i in range(0, len(mocked_blocks)):
        block = mocked_blocks[i]
        block_header = build_block_header(block)
        block_rlp = Data.from_bytes(block_header.raw_rlp()).to_ints()

        assert block_header.hash() == block["hash"]

        call = await decoder.test_decode_timestamp(block_rlp.length, block_rlp.values).call()
        output = Data.from_int(call.result.res)

        expected_output = Data.from_ints(getTimestamp(block_rlp))
        assert output == expected_output

@pytest.mark.asyncio
async def test_decode_base_fee(factory):
    starknet, decoder = factory

    for i in range(0, len(mocked_blocks)):
        block = mocked_blocks[i]
        block_header = build_block_header(block)
        block_rlp = Data.from_bytes(block_header.raw_rlp()).to_ints()

        assert block_header.hash() == block["hash"]

        call = await decoder.test_decode_base_fee(block_rlp.length, block_rlp.values).call()
        output = Data.from_int(call.result.res)

        expected_output = Data.from_ints(getBaseFee(block_rlp))
        assert output == expected_output
