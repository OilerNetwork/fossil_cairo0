import pytest
import asyncio

from typing import NamedTuple

from starkware.starkware_utils.error_handling import StarkException
from starkware.starknet.testing.starknet import Starknet
from starkware.starknet.testing.contract import StarknetContract
from starkware.cairo.lang.vm.crypto import pedersen_hash

from utils.types import Data
from utils.Signer import Signer
from utils.create_account import create_account
from utils.block_header import build_block_header

from mocks.blocks import mocked_blocks


class TestsDeps(NamedTuple):
    starknet: Starknet
    twap: StarknetContract
    account: StarknetContract
    signer: Signer
    l1_relayer_account: StarknetContract
    l1_relayer_signer: Signer
    storage_proof: StarknetContract

@pytest.fixture(scope='module')
def event_loop():
    return asyncio.new_event_loop()

async def submit_l1_parent_hash(l1_relayer_signer: Signer, l1_relayer_account: StarknetContract, storage_proof: StarknetContract, message = mocked_blocks[0]["parentHash"].hex(), block_number = mocked_blocks[0]['number']):
    message = Data.from_hex(message).to_ints()

    await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'receive_from_l1',
        [4] + message.values + [block_number]
    )

async def setup():
    starknet = await Starknet.empty()
    account, signer = await create_account(starknet)
    l1_relayer_account, l1_relayer_signer = await create_account(starknet)
    twap = await starknet.deploy(source="contracts/starknet/TWAP.cairo", cairo_path=["contracts"])
    storage_proof = await starknet.deploy(source="contracts/starknet/L1HeadersStore.cairo", cairo_path=["contracts"])

    await signer.send_transaction(
        account, storage_proof.contract_address, 'initialize', [l1_relayer_account.contract_address])

    await signer.send_transaction(
        account, twap.contract_address, 'initialize', [storage_proof.contract_address])

    await submit_l1_parent_hash(l1_relayer_signer, l1_relayer_account, storage_proof, mocked_blocks[0]['hash'].hex()[2:], mocked_blocks[0]['number'] + 1)

    return TestsDeps(
        starknet=starknet,
        twap=twap,
        account=account,
        signer=signer,
        l1_relayer_account=l1_relayer_account,
        l1_relayer_signer=l1_relayer_signer,
        storage_proof=storage_proof)

@pytest.fixture(scope='module')
async def factory():
    return await setup()

@pytest.mark.asyncio
async def test_initializer(factory):
    starknet, twap, account, signer, l1_relayer_account, l1_relayer_signer, storage_proof = factory
    pass

@pytest.mark.asyncio
async def test_register_computation(factory):
    starknet, twap, account, signer, l1_relayer_account, l1_relayer_signer, storage_proof = factory
    
    await signer.send_transaction(
        account,
        twap.contract_address,
        'register_computation',
        [mocked_blocks[0]['number'], 2, 3, 4]
    )

@pytest.mark.asyncio
async def test_compute_basefee_twap(factory):
    starknet, twap, account, signer, l1_relayer_account, l1_relayer_signer, storage_proof = factory
    callback_receiver = await starknet.deploy(source="contracts/starknet/mocks/CallbackReceiverMock.cairo", cairo_path=["contracts"])
    
    await signer.send_transaction(
        account,
        twap.contract_address,
        'register_computation',
        [mocked_blocks[0]['number'], mocked_blocks[0]['number'] - 2, 15, callback_receiver.contract_address])

    tmp_1 = pedersen_hash(mocked_blocks[0]['number'], mocked_blocks[0]['number'] - 2)
    tmp_2 = pedersen_hash(tmp_1, callback_receiver.contract_address)
    computation_id = pedersen_hash(tmp_2, 15)

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
            computation_id,
            3, # block headers lenghts in bytes length
            *[newer_block_rlp.length, older_block_rlp.length, oldest_block_rlp.length], # block headers lenghts in bytes
            3, # block headers lenghts in words length
            *[len(newer_block_rlp.values), len(older_block_rlp.values), len(oldest_block_rlp.values)], # block headers lenghts in words
            len([*newer_block_rlp.values, *older_block_rlp.values, *oldest_block_rlp.values]), # concat headers len
            *[*newer_block_rlp.values, *older_block_rlp.values, *oldest_block_rlp.values] # concat headers
        ]
    
    tx = await signer.send_transaction(
        account,
        twap.contract_address,
        'compute',
        calldata
    )

    print(f"Compute twap tx n_steps: {tx.call_info.execution_resources.n_steps}")

    computed_twap_call = await callback_receiver.twap().call()
    computed_twap = computed_twap_call.result.res

    (expected_twap, _) = divmod(newer_block['baseFeePerGas'] + older_block['baseFeePerGas'] + oldest_block['baseFeePerGas'], 3)

    assert computed_twap == expected_twap


@pytest.mark.asyncio
async def test_compute_difficulty_twap(factory):
    starknet, twap, account, signer, l1_relayer_account, l1_relayer_signer, storage_proof = factory
    callback_receiver = await starknet.deploy(source="contracts/starknet/mocks/CallbackReceiverMock.cairo", cairo_path=["contracts"])
    
    await signer.send_transaction(
        account,
        twap.contract_address,
        'register_computation',
        [mocked_blocks[0]['number'], mocked_blocks[0]['number'] - 2, 7, callback_receiver.contract_address])

    tmp_1 = pedersen_hash(mocked_blocks[0]['number'], mocked_blocks[0]['number'] - 2)
    tmp_2 = pedersen_hash(tmp_1, callback_receiver.contract_address)
    computation_id = pedersen_hash(tmp_2, 7)

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
            computation_id,
            3, # block headers lenghts in bytes length
            *[newer_block_rlp.length, older_block_rlp.length, oldest_block_rlp.length], # block headers lenghts in bytes
            3, # block headers lenghts in words length
            *[len(newer_block_rlp.values), len(older_block_rlp.values), len(oldest_block_rlp.values)], # block headers lenghts in words
            len([*newer_block_rlp.values, *older_block_rlp.values, *oldest_block_rlp.values]), # concat headers len
            *[*newer_block_rlp.values, *older_block_rlp.values, *oldest_block_rlp.values] # concat headers
        ]
    
    tx = await signer.send_transaction(
        account,
        twap.contract_address,
        'compute',
        calldata
    )

    print(f"Compute twap tx n_steps: {tx.call_info.execution_resources.n_steps}")

    computed_twap_call = await callback_receiver.twap().call()
    computed_twap = computed_twap_call.result.res

    difficulty_sum = newer_block['difficulty'] + older_block['difficulty'] + oldest_block['difficulty']

    (expected_twap, _) = divmod(difficulty_sum, 3)

    assert computed_twap == expected_twap


@pytest.mark.asyncio
async def test_compute_twap_gaps():
    starknet, twap, account, signer, l1_relayer_account, l1_relayer_signer, storage_proof = await setup()
    callback_receiver = await starknet.deploy(source="contracts/starknet/mocks/CallbackReceiverMock.cairo", cairo_path=["contracts"])
    
    await signer.send_transaction(
        account,
        twap.contract_address,
        'register_computation',
        [mocked_blocks[0]['number'], mocked_blocks[0]['number'] - 2, 7, callback_receiver.contract_address])

    tmp_1 = pedersen_hash(mocked_blocks[0]['number'], mocked_blocks[0]['number'] - 2)
    tmp_2 = pedersen_hash(tmp_1, callback_receiver.contract_address)
    computation_id = pedersen_hash(tmp_2, 7)

    newer_block = mocked_blocks[0]
    newer_block_header = build_block_header(newer_block)
    newer_block_rlp = Data.from_bytes(newer_block_header.raw_rlp()).to_ints()

    older_block = mocked_blocks[1]
    older_block_header = build_block_header(older_block)
    older_block_rlp = Data.from_bytes(older_block_header.raw_rlp()).to_ints()

    oldest_block = mocked_blocks[2]
    oldest_block_header = build_block_header(oldest_block)
    oldest_block_rlp = Data.from_bytes(oldest_block_header.raw_rlp()).to_ints()

    tx1_calldata = [
            computation_id,
            1, # block headers lenghts in bytes length
            *[newer_block_rlp.length], # block headers lenghts in bytes
            1, # block headers lenghts in words length
            *[len(newer_block_rlp.values)], # block headers lenghts in words
            len([*newer_block_rlp.values]), # concat headers len
            *[*newer_block_rlp.values] # concat headers
        ]
    
    tx1 = await signer.send_transaction(
        account,
        twap.contract_address,
        'compute',
        tx1_calldata
    )

    print(f"Compute twap tx1 n_steps: {tx1.call_info.execution_resources.n_steps}")

    tx2_calldata = [
            computation_id,
            2, # block headers lenghts in bytes length
            *[older_block_rlp.length, oldest_block_rlp.length], # block headers lenghts in bytes
            2, # block headers lenghts in words length
            *[len(older_block_rlp.values), len(oldest_block_rlp.values)], # block headers lenghts in words
            len([*older_block_rlp.values, *oldest_block_rlp.values]), # concat headers len
            *[*older_block_rlp.values, *oldest_block_rlp.values] # concat headers
        ]
    
    tx2 = await signer.send_transaction(
        account,
        twap.contract_address,
        'compute',
        tx2_calldata
    )

    print(f"Compute twap tx2 n_steps: {tx2.call_info.execution_resources.n_steps}")

    computed_twap_call = await callback_receiver.twap().call()
    computed_twap = computed_twap_call.result.res

    difficulty_sum = newer_block['difficulty'] + older_block['difficulty'] + oldest_block['difficulty']

    (expected_twap, _) = divmod(difficulty_sum, 3)

    assert computed_twap == expected_twap
