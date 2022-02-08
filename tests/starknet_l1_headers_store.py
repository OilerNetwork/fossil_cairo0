import pytest
import asyncio
from typing import NamedTuple

from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.testing.starknet import Starknet
from starkware.starkware_utils.error_handling import StarkException

from utils.Signer import Signer
from utils.block_header import build_block_header
from utils.create_account import create_account
from utils.helpers import chunk_bytes_input, bytes_to_int_little, IntsSequence
from utils.types import Data


from mocks.blocks import mocked_blocks

from utils.benchmarks.blockheader_rlp_extractor import (
    getBaseFee
)

class TestsDeps(NamedTuple):
    starknet: Starknet
    storage_proof: StarknetContract
    account: StarknetContract
    signer: Signer
    l1_relayer_account: StarknetContract
    l1_relayer_signer: Signer

@pytest.fixture(scope='module')
def event_loop():
    return asyncio.new_event_loop()

async def setup():
    starknet = await Starknet.empty()
    storage_proof = await starknet.deploy(source="contracts/starknet/L1HeadersStore.cairo", cairo_path=["contracts"])
    account, signer = await create_account(starknet)
    l1_relayer_account, l1_relayer_signer = await create_account(starknet)
    await signer.send_transaction(
        account, storage_proof.contract_address, 'initialize', [l1_relayer_account.contract_address])
    
    return TestsDeps(
        starknet=starknet,
        storage_proof=storage_proof,
        account=account,
        signer=signer,
        l1_relayer_account=l1_relayer_account,
        l1_relayer_signer=l1_relayer_signer
    )

@pytest.fixture(scope='module')
async def factory():
    return await setup()

async def submit_l1_parent_hash(l1_relayer_signer: Signer, l1_relayer_account: StarknetContract, storage_proof: StarknetContract):
    message = bytearray.fromhex(mocked_blocks[0]["parentHash"].hex()[2:])
    chunked_message = chunk_bytes_input(message)
    formatted_words = list(map(bytes_to_int_little, chunked_message))

    await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'receive_from_l1',
        [len(formatted_words)] + formatted_words + [mocked_blocks[0]['number']]
    )


@pytest.mark.asyncio
async def test_submit_hash(factory):
    starknet, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = factory
    # Submit message using l1_relayer_account
    await submit_l1_parent_hash(l1_relayer_signer, l1_relayer_account, storage_proof)


@pytest.mark.asyncio
async def test_process_block(factory):
    starknet, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = factory

    await submit_l1_parent_hash(l1_relayer_signer, l1_relayer_account, storage_proof)

    block = mocked_blocks[1]
    block_header = build_block_header(block)
    block_rlp = Data.from_bytes(block_header.raw_rlp()).to_ints()

    await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'process_block',
        [0] + [block_rlp.length] + [block['number']] + [len(block_rlp.values)] + block_rlp.values
    )

    set_block_parent_hash_call = await storage_proof.get_parent_hash(block['number']).call()
    set_parent_hash = Data.from_ints(IntsSequence(list(set_block_parent_hash_call.result.res), 32))

    assert set_parent_hash.to_hex() == block["parentHash"].hex()

@pytest.mark.asyncio
async def test_process_invalid_block(factory):
    starknet, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = factory

    await submit_l1_parent_hash(l1_relayer_signer, l1_relayer_account, storage_proof)

    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = Data.from_bytes(block_header.raw_rlp()).to_ints()

    with pytest.raises(StarkException):
        await l1_relayer_signer.send_transaction(
            l1_relayer_account,
            storage_proof.contract_address,
            'process_block',
            [0] + [block_rlp.length] + [block['number']] + [len(block_rlp.values)] + block_rlp.values
        )


@pytest.mark.asyncio
async def test_set_state_root(factory):
    starknet, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = factory

    await submit_l1_parent_hash(l1_relayer_signer, l1_relayer_account, storage_proof)

    block = mocked_blocks[1]
    block_header = build_block_header(block)
    block_rlp = Data.from_bytes(block_header.raw_rlp()).to_ints()

    await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'process_block',
        [int("100000000", 2)] + [block_rlp.length] + [block['number']] + [len(block_rlp.values)] + block_rlp.values
    )

    set_state_root_call = await storage_proof.get_state_root(block['number']).call()
    set_state_root = Data.from_ints(IntsSequence(list(set_state_root_call.result.res), 32))

    assert set_state_root.to_hex() == block["stateRoot"].hex()


@pytest.mark.asyncio
async def test_set_transactions_root(factory):
    starknet, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = factory

    await submit_l1_parent_hash(l1_relayer_signer, l1_relayer_account, storage_proof)

    block = mocked_blocks[1]
    block_header = build_block_header(block)
    block_rlp = Data.from_bytes(block_header.raw_rlp()).to_ints()

    await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'process_block',
        [int("010000000", 2)] + [block_rlp.length] + [block['number']] + [len(block_rlp.values)] + block_rlp.values
    )

    set_txns_root_call = await storage_proof.get_transactions_root(block['number']).call()
    set_txns_root = Data.from_ints(IntsSequence(list(set_txns_root_call.result.res), 32))
    assert set_txns_root.to_hex() == block["transactionsRoot"].hex()

@pytest.mark.asyncio
async def test_set_receipts_root(factory):
    starknet, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = factory

    await submit_l1_parent_hash(l1_relayer_signer, l1_relayer_account, storage_proof)

    block = mocked_blocks[1]
    block_header = build_block_header(block)
    block_rlp = Data.from_bytes(block_header.raw_rlp()).to_ints()

    await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'process_block',
        [int("001000000", 2)] + [block_rlp.length] + [block['number']] + [len(block_rlp.values)] + block_rlp.values
    )

    set_receipts_root_call = await storage_proof.get_receipts_root(block['number']).call()
    set_receipts_root = Data.from_ints(IntsSequence(list(set_receipts_root_call.result.res), 32))
    assert set_receipts_root.to_hex() == block["receiptsRoot"].hex()

@pytest.mark.asyncio
async def test_set_uncles_hash(factory):
    starknet, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = factory

    await submit_l1_parent_hash(l1_relayer_signer, l1_relayer_account, storage_proof)

    block = mocked_blocks[1]
    block_header = build_block_header(block)
    block_rlp = Data.from_bytes(block_header.raw_rlp()).to_ints()

    await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'process_block',
        [int("000100000", 2)] + [block_rlp.length] + [block['number']] + [len(block_rlp.values)] + block_rlp.values
    )

    set_uncles_hash_call = await storage_proof.get_uncles_hash(block['number']).call()
    set_uncles_hash = Data.from_ints(IntsSequence(list(set_uncles_hash_call.result.res), 32))
    assert set_uncles_hash.to_hex() == block["sha3Uncles"].hex()

@pytest.mark.asyncio
async def test_set_beneficiary(factory):
    starknet, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = factory

    await submit_l1_parent_hash(l1_relayer_signer, l1_relayer_account, storage_proof)

    block = mocked_blocks[1]
    block_header = build_block_header(block)
    block_rlp = Data.from_bytes(block_header.raw_rlp()).to_ints()

    await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'process_block',
        [int("000001000", 2)] + [block_rlp.length] + [block['number']] + [len(block_rlp.values)] + block_rlp.values
    )

    set_beneficiary_call = await storage_proof.get_beneficiary(block['number']).call()
    set_beneficiary = Data.from_ints(IntsSequence(list(set_beneficiary_call.result.res), 20))
    assert set_beneficiary == Data.from_hex(block["miner"])


@pytest.mark.asyncio
async def test_set_difficulty(factory):
    starknet, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = factory

    await submit_l1_parent_hash(l1_relayer_signer, l1_relayer_account, storage_proof)

    block = mocked_blocks[1]
    block_header = build_block_header(block)
    block_rlp = Data.from_bytes(block_header.raw_rlp()).to_ints()

    await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'process_block',
        [int("000010000", 2)] + [block_rlp.length] + [block['number']] + [len(block_rlp.values)] + block_rlp.values
    )

    set_difficulty_call = await storage_proof.get_difficulty(block['number']).call()
    set_difficulty = set_difficulty_call.result.res
    assert set_difficulty == block["difficulty"]


@pytest.mark.asyncio
async def test_set_base_fee(factory):
    starknet, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = factory

    await submit_l1_parent_hash(l1_relayer_signer, l1_relayer_account, storage_proof)

    block = mocked_blocks[1]
    block_header = build_block_header(block)
    block_rlp = Data.from_bytes(block_header.raw_rlp()).to_ints()

    await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'process_block',
        [int("000000100", 2)] + [block_rlp.length] + [block['number']] + [len(block_rlp.values)] + block_rlp.values
    )

    set_base_fee_call = await storage_proof.get_base_fee(block['number']).call()
    set_base_fee = set_base_fee_call.result.res
    assert set_base_fee == block["baseFeePerGas"]


@pytest.mark.asyncio
async def test_set_timestamp(factory):
    starknet, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = factory

    await submit_l1_parent_hash(l1_relayer_signer, l1_relayer_account, storage_proof)

    block = mocked_blocks[1]
    block_header = build_block_header(block)
    block_rlp = Data.from_bytes(block_header.raw_rlp()).to_ints()

    await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'process_block',
        [int("000000010", 2)] + [block_rlp.length] + [block['number']] + [len(block_rlp.values)] + block_rlp.values
    )

    set_timestamp_call = await storage_proof.get_timestamp(block['number']).call()
    set_timestamp = set_timestamp_call.result.res
    assert set_timestamp == block['timestamp']


@pytest.mark.asyncio
async def test_set_gas_used(factory):
    starknet, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = factory

    await submit_l1_parent_hash(l1_relayer_signer, l1_relayer_account, storage_proof)

    block = mocked_blocks[1]
    block_header = build_block_header(block)
    block_rlp = Data.from_bytes(block_header.raw_rlp()).to_ints()

    await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'process_block',
        [int("000000001", 2)] + [block_rlp.length] + [block['number']] + [len(block_rlp.values)] + block_rlp.values
    )

    set_gas_used_call = await storage_proof.get_gas_used(block['number']).call()
    set_gas_used = set_gas_used_call.result.res
    assert set_gas_used == block['gasUsed']

    