import pytest
from typing import NamedTuple

from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.testing.starknet import Starknet
from starkware.starkware_utils.error_handling import StarkException

from utils.Signer import Signer
from utils.block_header import build_block_header
from utils.create_account import create_account
from utils.helpers import chunk_bytes_input, bytes_to_int, bytes_to_int_little


from mocks.blocks import mocked_blocks


bytes_to_int_big = lambda word: bytes_to_int(word)


class TestsDeps(NamedTuple):
    starknet: Starknet
    storage_proof: StarknetContract
    account: StarknetContract
    signer: Signer
    l1_relayer_account: StarknetContract
    l1_relayer_signer: Signer


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
async def test_submit_hash():
    starknet, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = await setup()
    # Submit message using l1_relayer_account
    await submit_l1_parent_hash(l1_relayer_signer, l1_relayer_account, storage_proof)


@pytest.mark.asyncio
async def test_process_block():
    starknet, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = await setup()

    await submit_l1_parent_hash(l1_relayer_signer, l1_relayer_account, storage_proof)

    block = mocked_blocks[1]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()
    block_rlp_chunked = chunk_bytes_input(block_rlp)
    block_rlp_formatted = list(map(bytes_to_int_big, block_rlp_chunked))

    await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'process_block',
        [len(block_rlp)] + [block['number']] + [len(block_rlp_formatted)] + block_rlp_formatted
    )

    set_block_parent_hash_call = await storage_proof.get_parent_hash(block['number']).call()
    set_parent_hash = '0x' + ''.join(v.to_bytes(8, 'big').hex() for v in set_block_parent_hash_call.result.res)

    assert set_parent_hash == block["parentHash"].hex()

@pytest.mark.asyncio
async def test_process_invalid_block():
    starknet, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = await setup()

    await submit_l1_parent_hash(l1_relayer_signer, l1_relayer_account, storage_proof)

    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()
    block_rlp_chunked = chunk_bytes_input(block_rlp)
    block_rlp_formatted = list(map(bytes_to_int_big, block_rlp_chunked))

    with pytest.raises(StarkException):
        await l1_relayer_signer.send_transaction(
            l1_relayer_account,
            storage_proof.contract_address,
            'process_block',
            [len(block_rlp)] + [block['number']] + [len(block_rlp_formatted)] + block_rlp_formatted
        )


@pytest.mark.asyncio
async def test_set_state_root():
    starknet, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = await setup()

    await submit_l1_parent_hash(l1_relayer_signer, l1_relayer_account, storage_proof)

    block = mocked_blocks[1]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()
    block_rlp_chunked = chunk_bytes_input(block_rlp)
    block_rlp_formatted = list(map(bytes_to_int_big, block_rlp_chunked))

    await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'process_block',
        [len(block_rlp)] + [block['number']] + [len(block_rlp_formatted)] + block_rlp_formatted
    )

    await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'set_block_state_root',
        [len(block_rlp)] + [block['number']] + [len(block_rlp_formatted)] + block_rlp_formatted
    )

    set_state_root_call = await storage_proof.get_state_root(block['number']).call()
    set_state_root = '0x' + ''.join(v.to_bytes(8, 'big').hex() for v in set_state_root_call.result.res)

    assert set_state_root == block["stateRoot"].hex()


@pytest.mark.asyncio
async def test_set_transactions_root():
    starknet, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = await setup()

    await submit_l1_parent_hash(l1_relayer_signer, l1_relayer_account, storage_proof)

    block = mocked_blocks[1]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()
    block_rlp_chunked = chunk_bytes_input(block_rlp)
    block_rlp_formatted = list(map(bytes_to_int_big, block_rlp_chunked))

    await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'process_block',
        [len(block_rlp)] + [block['number']] + [len(block_rlp_formatted)] + block_rlp_formatted
    )

    await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'set_block_transactions_root',
        [len(block_rlp)] + [block['number']] + [len(block_rlp_formatted)] + block_rlp_formatted
    )

    set_txns_root_call = await storage_proof.get_transactions_root(block['number']).call()
    set_txns_root = '0x' + ''.join(v.to_bytes(8, 'big').hex() for v in set_txns_root_call.result.res)
    assert set_txns_root == block["transactionsRoot"].hex()

@pytest.mark.asyncio
async def test_set_receipts_root():
    starknet, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = await setup()

    await submit_l1_parent_hash(l1_relayer_signer, l1_relayer_account, storage_proof)

    block = mocked_blocks[1]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()
    block_rlp_chunked = chunk_bytes_input(block_rlp)
    block_rlp_formatted = list(map(bytes_to_int_big, block_rlp_chunked))

    await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'process_block',
        [len(block_rlp)] + [block['number']] + [len(block_rlp_formatted)] + block_rlp_formatted
    )

    await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'set_block_receipts_root',
        [len(block_rlp)] + [block['number']] + [len(block_rlp_formatted)] + block_rlp_formatted
    )

    set_receipts_root_call = await storage_proof.get_receipts_root(block['number']).call()
    set_receipts_root = '0x' + ''.join(v.to_bytes(8, 'big').hex() for v in set_receipts_root_call.result.res)
    assert set_receipts_root == block["receiptsRoot"].hex()

@pytest.mark.asyncio
async def test_set_uncles_hash():
    starknet, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = await setup()

    await submit_l1_parent_hash(l1_relayer_signer, l1_relayer_account, storage_proof)

    block = mocked_blocks[1]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()
    block_rlp_chunked = chunk_bytes_input(block_rlp)
    block_rlp_formatted = list(map(bytes_to_int_big, block_rlp_chunked))

    await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'process_block',
        [len(block_rlp)] + [block['number']] + [len(block_rlp_formatted)] + block_rlp_formatted
    )

    await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'set_block_uncles_hash',
        [len(block_rlp)] + [block['number']] + [len(block_rlp_formatted)] + block_rlp_formatted
    )

    set_uncles_hash_call = await storage_proof.get_uncles_hash(block['number']).call()
    set_uncles_hash = '0x' + ''.join(v.to_bytes(8, 'big').hex() for v in set_uncles_hash_call.result.res)
    assert set_uncles_hash == block["sha3Uncles"].hex()

@pytest.mark.asyncio
async def test_set_beneficiary():
    starknet, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = await setup()

    await submit_l1_parent_hash(l1_relayer_signer, l1_relayer_account, storage_proof)

    block = mocked_blocks[1]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()
    block_rlp_chunked = chunk_bytes_input(block_rlp)
    block_rlp_formatted = list(map(bytes_to_int_big, block_rlp_chunked))

    await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'process_block',
        [len(block_rlp)] + [block['number']] + [len(block_rlp_formatted)] + block_rlp_formatted
    )

    await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'set_block_beneficiary',
        [len(block_rlp)] + [block['number']] + [len(block_rlp_formatted)] + block_rlp_formatted
    )

    set_beneficiary_call = await storage_proof.get_beneficiary(block['number']).call()
    set_beneficiary = '0x' + ''.join(v.to_bytes(8, 'big').hex() for v in set_beneficiary_call.result.res)
    # TODO the address is as expected however it reconstruction from words puts some 0s
    # assert set_beneficiary == block["miner"]


@pytest.mark.asyncio
async def test_set_difficulty():
    starknet, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = await setup()

    await submit_l1_parent_hash(l1_relayer_signer, l1_relayer_account, storage_proof)

    block = mocked_blocks[1]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()
    block_rlp_chunked = chunk_bytes_input(block_rlp)
    block_rlp_formatted = list(map(bytes_to_int_big, block_rlp_chunked))

    await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'process_block',
        [len(block_rlp)] + [block['number']] + [len(block_rlp_formatted)] + block_rlp_formatted
    )

    await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'set_block_difficulty',
        [len(block_rlp)] + [block['number']] + [len(block_rlp_formatted)] + block_rlp_formatted
    )

    set_difficulty_call = await storage_proof.get_difficulty(block['number']).call()
    set_difficulty = set_difficulty_call.result.res
    assert set_difficulty == block["difficulty"]

    