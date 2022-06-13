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
from utils.types import Data, BlockHeaderIndexes


from mocks.blocks import mocked_blocks


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

async def submit_l1_parent_hash(l1_relayer_signer: Signer, l1_relayer_account: StarknetContract, storage_proof: StarknetContract, message = mocked_blocks[0]["parentHash"].hex(), block_number = mocked_blocks[0]['number']):
    message = Data.from_hex(message).to_ints()

    tx = await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'receive_from_l1',
        [4] + message.values + [block_number]
    )

    return tx.call_info.execution_resources.n_steps

@pytest.mark.asyncio
async def test_submit_hash(factory):
    starknet, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = factory
    # Submit message using l1_relayer_account
    n_steps = await submit_l1_parent_hash(l1_relayer_signer, l1_relayer_account, storage_proof)

    print(f"Execution number of steps: {n_steps}")

@pytest.mark.asyncio
async def test_submit_hash_update_latest_block(factory):
    starknet, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = await setup()

    block_number = 10

    original_latest = (await storage_proof.get_latest_l1_block().call()).result.res

    assert original_latest == 0

    # Submit message using l1_relayer_account
    n_steps = await submit_l1_parent_hash(
        l1_relayer_signer,
        l1_relayer_account,
        storage_proof,
        mocked_blocks[0]["parentHash"].hex(),
        block_number)

    current_latest = (await storage_proof.get_latest_l1_block().call()).result.res

    assert current_latest == block_number 

    print(f"Execution number of steps: {n_steps}")

@pytest.mark.asyncio
async def test_process_block(factory):
    starknet, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = factory

    await submit_l1_parent_hash(l1_relayer_signer, l1_relayer_account, storage_proof)

    block = mocked_blocks[1]
    block_header = build_block_header(block)
    block_rlp = Data.from_bytes(block_header.raw_rlp()).to_ints()

    tx = await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'process_block',
        [0] + [block['number']] + [block_rlp.length] + [len(block_rlp.values)] + block_rlp.values
    )

    set_block_parent_hash_call = await storage_proof.get_parent_hash(block['number']).call()
    set_parent_hash = Data.from_ints(IntsSequence(list(set_block_parent_hash_call.result.res), 32))

    assert set_parent_hash.to_hex() == block["parentHash"].hex()

    print(f"Execution number of steps: {tx.call_info.execution_resources.n_steps}")

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
            [0] + [block['number']] + [block_rlp.length] + [len(block_rlp.values)] + block_rlp.values
        )

@pytest.mark.asyncio
async def test_set_uncles_hash(factory):
    starknet, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = factory

    await submit_l1_parent_hash(l1_relayer_signer, l1_relayer_account, storage_proof)

    block = mocked_blocks[1]
    block_header = build_block_header(block)
    block_rlp = Data.from_bytes(block_header.raw_rlp()).to_ints()

    tx = await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'process_block',
        [2**BlockHeaderIndexes.OMMERS_HASH] + [block['number']] + [block_rlp.length] + [len(block_rlp.values)] + block_rlp.values
    )

    set_uncles_hash_call = await storage_proof.get_uncles_hash(block['number']).call()
    set_uncles_hash = Data.from_ints(IntsSequence(list(set_uncles_hash_call.result.res), 32))
    assert set_uncles_hash.to_hex() == block["sha3Uncles"].hex()

    print(f"Execution number of steps: {tx.call_info.execution_resources.n_steps}")

@pytest.mark.asyncio
async def test_set_beneficiary(factory):
    starknet, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = factory

    await submit_l1_parent_hash(l1_relayer_signer, l1_relayer_account, storage_proof)

    block = mocked_blocks[1]
    block_header = build_block_header(block)
    block_rlp = Data.from_bytes(block_header.raw_rlp()).to_ints()

    tx = await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'process_block',
        [2**BlockHeaderIndexes.BENEFICIARY] + [block['number']] + [block_rlp.length] + [len(block_rlp.values)] + block_rlp.values
    )

    set_beneficiary_call = await storage_proof.get_beneficiary(block['number']).call()
    set_beneficiary = Data.from_ints(IntsSequence(list(set_beneficiary_call.result.res), 20))
    assert set_beneficiary == Data.from_hex(block["miner"])

    print(f"Execution number of steps: {tx.call_info.execution_resources.n_steps}")

@pytest.mark.asyncio
async def test_set_state_root(factory):
    starknet, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = factory

    await submit_l1_parent_hash(l1_relayer_signer, l1_relayer_account, storage_proof)

    block = mocked_blocks[1]
    block_header = build_block_header(block)
    block_rlp = Data.from_bytes(block_header.raw_rlp()).to_ints()

    tx = await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'process_block',        
        [2**BlockHeaderIndexes.STATE_ROOT] + [block['number']] + [block_rlp.length] + [len(block_rlp.values)] + block_rlp.values
    )

    set_state_root_call = await storage_proof.get_state_root(block['number']).call()
    set_state_root = Data.from_ints(IntsSequence(list(set_state_root_call.result.res), 32))

    assert set_state_root.to_hex() == block["stateRoot"].hex()

    print(f"Execution number of steps: {tx.call_info.execution_resources.n_steps}")


@pytest.mark.asyncio
async def test_set_transactions_root(factory):
    starknet, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = factory

    await submit_l1_parent_hash(l1_relayer_signer, l1_relayer_account, storage_proof)

    block = mocked_blocks[1]
    block_header = build_block_header(block)
    block_rlp = Data.from_bytes(block_header.raw_rlp()).to_ints()

    tx = await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'process_block',
        [2**BlockHeaderIndexes.TRANSACTION_ROOT] + [block['number']] + [block_rlp.length] + [len(block_rlp.values)] + block_rlp.values
    )

    set_txns_root_call = await storage_proof.get_transactions_root(block['number']).call()
    set_txns_root = Data.from_ints(IntsSequence(list(set_txns_root_call.result.res), 32))
    assert set_txns_root.to_hex() == block["transactionsRoot"].hex()

    print(f"Execution number of steps: {tx.call_info.execution_resources.n_steps}")

@pytest.mark.asyncio
async def test_set_receipts_root(factory):
    starknet, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = factory

    await submit_l1_parent_hash(l1_relayer_signer, l1_relayer_account, storage_proof)

    block = mocked_blocks[1]
    block_header = build_block_header(block)
    block_rlp = Data.from_bytes(block_header.raw_rlp()).to_ints()

    tx = await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'process_block',
        [2**BlockHeaderIndexes.RECEIPTS_ROOT] + [block['number']] + [block_rlp.length] + [len(block_rlp.values)] + block_rlp.values
    )

    set_receipts_root_call = await storage_proof.get_receipts_root(block['number']).call()
    set_receipts_root = Data.from_ints(IntsSequence(list(set_receipts_root_call.result.res), 32))
    assert set_receipts_root.to_hex() == block["receiptsRoot"].hex()

    print(f"Execution number of steps: {tx.call_info.execution_resources.n_steps}")
    
@pytest.mark.asyncio
async def test_set_difficulty(factory):
    starknet, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = factory

    await submit_l1_parent_hash(l1_relayer_signer, l1_relayer_account, storage_proof)

    block = mocked_blocks[1]
    block_header = build_block_header(block)
    block_rlp = Data.from_bytes(block_header.raw_rlp()).to_ints()

    tx = await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'process_block',
        [2**BlockHeaderIndexes.DIFFICULTY] + [block['number']] + [block_rlp.length] + [len(block_rlp.values)] + block_rlp.values
    )

    set_difficulty_call = await storage_proof.get_difficulty(block['number']).call()
    set_difficulty = set_difficulty_call.result.res
    assert set_difficulty == block["difficulty"]

    print(f"Execution number of steps: {tx.call_info.execution_resources.n_steps}")

@pytest.mark.asyncio
async def test_set_gas_used(factory):
    starknet, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = factory

    await submit_l1_parent_hash(l1_relayer_signer, l1_relayer_account, storage_proof)

    block = mocked_blocks[1]
    block_header = build_block_header(block)
    block_rlp = Data.from_bytes(block_header.raw_rlp()).to_ints()

    tx = await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'process_block',
        [2**BlockHeaderIndexes.GAS_USED] + [block['number']] + [block_rlp.length] + [len(block_rlp.values)] + block_rlp.values
    )

    set_gas_used_call = await storage_proof.get_gas_used(block['number']).call()
    set_gas_used = set_gas_used_call.result.res
    assert set_gas_used == block['gasUsed']

    print(f"Execution number of steps: {tx.call_info.execution_resources.n_steps}")

@pytest.mark.asyncio
async def test_set_timestamp(factory):
    starknet, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = factory

    await submit_l1_parent_hash(l1_relayer_signer, l1_relayer_account, storage_proof)

    block = mocked_blocks[1]
    block_header = build_block_header(block)
    block_rlp = Data.from_bytes(block_header.raw_rlp()).to_ints()

    tx = await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'process_block',
        [2**BlockHeaderIndexes.TIMESTAMP] + [block['number']] + [block_rlp.length] + [len(block_rlp.values)] + block_rlp.values
    )

    set_timestamp_call = await storage_proof.get_timestamp(block['number']).call()
    set_timestamp = set_timestamp_call.result.res
    assert set_timestamp == block['timestamp']

    print(f"Execution number of steps: {tx.call_info.execution_resources.n_steps}")

@pytest.mark.asyncio
async def test_set_base_fee(factory):
    starknet, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = factory

    await submit_l1_parent_hash(l1_relayer_signer, l1_relayer_account, storage_proof)

    block = mocked_blocks[1]
    block_header = build_block_header(block)
    block_rlp = Data.from_bytes(block_header.raw_rlp()).to_ints()

    tx = await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'process_block',
        [2**BlockHeaderIndexes.BASE_FEE] + [block['number']] + [block_rlp.length] + [len(block_rlp.values)] + block_rlp.values
    )

    set_base_fee_call = await storage_proof.get_base_fee(block['number']).call()
    set_base_fee = set_base_fee_call.result.res
    assert set_base_fee == block["baseFeePerGas"]

    print(f"Execution number of steps: {tx.call_info.execution_resources.n_steps}")


@pytest.mark.asyncio
async def test_process_till_block():
    starknet, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = await setup()

    await submit_l1_parent_hash(l1_relayer_signer, l1_relayer_account, storage_proof, mocked_blocks[0]['hash'].hex()[2:], mocked_blocks[0]['number'] + 1)

    newer_block = mocked_blocks[0]
    newer_block_header = build_block_header(newer_block)
    newer_block_rlp = Data.from_bytes(newer_block_header.raw_rlp()).to_ints()

    older_block = mocked_blocks[1]
    older_block_header = build_block_header(older_block)
    older_block_rlp = Data.from_bytes(older_block_header.raw_rlp()).to_ints()

    oldest_block = mocked_blocks[2]
    oldest_block_header = build_block_header(oldest_block)
    oldest_block_rlp = Data.from_bytes(oldest_block_header.raw_rlp()).to_ints()

    calldata = [
            2**BlockHeaderIndexes.STATE_ROOT, # options set
            newer_block['number'] + 1, # start_block_number
            3, # block headers lenghts in bytes length
            *[newer_block_rlp.length, older_block_rlp.length, oldest_block_rlp.length], # block headers lenghts in bytes
            3, # block headers lenghts in words length
            *[len(newer_block_rlp.values), len(older_block_rlp.values), len(oldest_block_rlp.values)], # block headers lenghts in words
            len([*newer_block_rlp.values, *older_block_rlp.values, *oldest_block_rlp.values]), # concat headers len
            *[*newer_block_rlp.values, *older_block_rlp.values, *oldest_block_rlp.values] # concat headers
        ]
    
    tx = await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'process_till_block',
        calldata
    )

    newer_block_parent_hash_call = await storage_proof.get_parent_hash(newer_block['number']).call()
    newer_block_parent_hash = Data.from_ints(IntsSequence(list(newer_block_parent_hash_call.result.res), 32))
    assert newer_block_parent_hash.to_hex() == '0x0000000000000000000000000000000000000000000000000000000000000000'

    set_state_root_call = await storage_proof.get_state_root(oldest_block['number']).call()
    set_state_root = Data.from_ints(IntsSequence(list(set_state_root_call.result.res), 32))
    assert set_state_root.to_hex() == oldest_block["stateRoot"].hex()

    print(f"Execution number of steps: {tx.call_info.execution_resources.n_steps}")



    