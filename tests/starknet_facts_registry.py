import pytest
import asyncio
from typing import NamedTuple

from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.testing.starknet import Starknet
from starkware.starkware_utils.error_handling import StarkException

from utils.types import Data, BlockHeaderIndexes
from utils.Signer import Signer
from utils.create_account import create_account
from utils.helpers import chunk_bytes_input, bytes_to_int, Encoding, IntsSequence
from utils.block_header import build_block_header

from mocks.blocks import mocked_blocks
from mocks.trie_proofs import trie_proofs


bytes_to_int_big = lambda word: bytes_to_int(word)

class BaseTestsDeps(NamedTuple):
    starknet: Starknet
    facts_registry: StarknetContract
    account: StarknetContract
    signer: Signer

class RegistryTestsDeps(NamedTuple):
    starknet: Starknet
    facts_registry: StarknetContract
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
    facts_registry = await starknet.deploy(source="contracts/starknet/FactsRegistry.cairo", cairo_path=["contracts"])
    account, signer = await create_account(starknet)

    return BaseTestsDeps(
        starknet=starknet,
        facts_registry=facts_registry,
        account=account,
        signer=signer)

@pytest.fixture(scope='module')
async def base_factory():
    return await setup()

@pytest.fixture(scope='module')
async def registry_initialized():
    starknet, facts_registry, account, signer = await setup()

    storage_proof = await starknet.deploy(source="contracts/starknet/L1HeadersStore.cairo", cairo_path=["contracts"])
    l1_relayer_account, l1_relayer_signer = await create_account(starknet)

    await signer.send_transaction(
        account, storage_proof.contract_address, 'initialize', [l1_relayer_account.contract_address])

    await signer.send_transaction(
        account, facts_registry.contract_address, 'initialize', [storage_proof.contract_address])

    block = mocked_blocks[3]
    block_header = build_block_header(block)
    block_rlp = Data.from_bytes(block_header.raw_rlp()).to_ints()

    block_parent_hash = Data.from_hex("0x62a8a05ef6fcd39a11b2d642d4b7ab177056e1eb4bde4454f67285164ef8ce65")
    assert block_parent_hash.to_hex() == block_header.hash().hex()

    # Submit blockhash from L1
    await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'receive_from_l1',
        [len(block_parent_hash.to_ints(Encoding.BIG).values)] + block_parent_hash.to_ints(Encoding.BIG).values + [mocked_blocks[3]['number'] + 1])

    await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'process_block',        
        [2**BlockHeaderIndexes.STATE_ROOT] + [block['number']] + [block_rlp.length] + [len(block_rlp.values)] + block_rlp.values
    )

    return RegistryTestsDeps(
        starknet=starknet,
        facts_registry=facts_registry,
        storage_proof=storage_proof,
        account=account,
        signer=signer,
        l1_relayer_account=l1_relayer_account,
        l1_relayer_signer=l1_relayer_signer
    )


@pytest.mark.asyncio
async def test_initializer(base_factory):
    starknet, facts_registry, account, signer = base_factory

    l1_headers_store_addr = 0xbeaf

    await signer.send_transaction(
        account, facts_registry.contract_address, 'initialize', [l1_headers_store_addr])

    # Ensure address has been correctly set
    get_l1_headers_store_addr_call = await facts_registry.get_l1_headers_store_addr().call()
    set_l1_headers_store_addr = get_l1_headers_store_addr_call.result.res
    assert set_l1_headers_store_addr == l1_headers_store_addr

    # Ensure contract can't be initialized one more time
    with pytest.raises(StarkException):
        await signer.send_transaction(
            account, facts_registry.contract_address, 'initialize', [l1_headers_store_addr])


@pytest.mark.asyncio
async def test_prove_account(registry_initialized):
    starknet, facts_registry, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = registry_initialized

    proof = list(map(lambda element: Data.from_hex(element).to_ints(), trie_proofs[1]['accountProof']))
    flat_proof = []
    flat_proof_sizes_bytes = []
    flat_proof_sizes_words = []
    for proof_element in proof:
        flat_proof += proof_element.values
        flat_proof_sizes_bytes += [proof_element.length]
        flat_proof_sizes_words += [len(proof_element.values)]

    options_set = 15 # saves everything in state

    l1_account_address = Data.from_hex(trie_proofs[1]['address'])
    account_words64 = l1_account_address.to_ints()

    set_state_root_call = await storage_proof.get_state_root(mocked_blocks[3]['number']).call()
    set_state_root = set_state_root_call.result.res

    tx = await signer.send_transaction(
        account,
        facts_registry.contract_address,
        "prove_account",
        [
            options_set,
            mocked_blocks[3]['number'],
            account_words64.values[0],
            account_words64.values[1],
            account_words64.values[2],
            len(flat_proof_sizes_bytes)] +
            flat_proof_sizes_bytes +
            [len(flat_proof_sizes_words)] +
            flat_proof_sizes_words +
            [len(flat_proof)] +
            flat_proof)

    print(f"Prove account, execution number of steps: {tx.call_info.cairo_usage.n_steps}")

    get_storage_hash_call = await facts_registry.get_verified_account_storage_hash(
        int(l1_account_address.to_hex()[2:], 16),
        mocked_blocks[3]['number']).call()
    set_storage_hash = get_storage_hash_call.result.res

    get_code_hash_call = await facts_registry.get_verified_account_code_hash(
        int(l1_account_address.to_hex()[2:], 16),
        mocked_blocks[3]['number']).call()
    set_code_hash = get_code_hash_call.result.res

    get_balance_call = await facts_registry.get_verified_account_balance(
        int(l1_account_address.to_hex()[2:], 16),
        mocked_blocks[3]['number']).call()
    set_balance = get_balance_call.result.res

    get_nonce_call = await facts_registry.get_verified_account_nonce(
        int(l1_account_address.to_hex()[2:], 16),
        mocked_blocks[3]['number']).call()
    set_nonce = get_nonce_call.result.res

    assert set_nonce == int(trie_proofs[1]['nonce'][2:], 16)
    assert set_balance == int(trie_proofs[1]['balance'][2:], 16)
    assert Data.from_ints(IntsSequence(list(set_storage_hash), 32)).to_hex() == trie_proofs[1]['storageHash']
    assert Data.from_ints(IntsSequence(list(set_code_hash), 32)).to_hex() == trie_proofs[1]['codeHash']

@pytest.mark.asyncio
async def test_get_storage(registry_initialized):
    starknet, facts_registry, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = registry_initialized

    account_proof = list(map(lambda element: Data.from_hex(element).to_ints(), trie_proofs[2]['accountProof']))
    flat_account_proof = []
    flat_account_proof_sizes_bytes = []
    flat_account_proof_sizes_words = []
    for proof_element in account_proof:
        flat_account_proof += proof_element.values
        flat_account_proof_sizes_bytes += [proof_element.length]
        flat_account_proof_sizes_words += [len(proof_element.values)]

    options_set = 15 # saves everything in state

    l1_account_address = Data.from_hex(trie_proofs[1]['address'])
    account_words64 = l1_account_address.to_ints()

    tx = await signer.send_transaction(
        account,
        facts_registry.contract_address,
        "prove_account",
        [
            options_set,
            mocked_blocks[3]['number'],
            account_words64.values[0],
            account_words64.values[1],
            account_words64.values[2],
            len(flat_account_proof_sizes_bytes)] +
            flat_account_proof_sizes_bytes +
            [len(flat_account_proof_sizes_words)] +
            flat_account_proof_sizes_words +
            [len(flat_account_proof)] +
            flat_account_proof)

    print(f"Prove account, execution number of steps: {tx.call_info.cairo_usage.n_steps}")

    slot = Data.from_hex(trie_proofs[2]['storageProof'][0]['key']).to_ints()

    storage_proof = list(map(lambda element: Data.from_hex(element).to_ints(), trie_proofs[2]['storageProof'][0]['proof']))
    flat_storage_proof = []
    flat_storage_proof_sizes_bytes = []
    flat_storage_proof_sizes_words = []
    for proof_element in storage_proof:
        flat_storage_proof += proof_element.values
        flat_storage_proof_sizes_bytes += [proof_element.length]
        flat_storage_proof_sizes_words += [len(proof_element.values)]

    get_balance_call = await facts_registry.get_storage(
        mocked_blocks[3]['number'],
        int(trie_proofs[2]['address'][2:], 16),
        tuple(slot.values),
        flat_storage_proof_sizes_bytes,
        flat_storage_proof_sizes_words,
        flat_storage_proof).call()

    print(f"Get balance call n_steps: {get_balance_call.call_info.cairo_usage.n_steps}")
    
    result = Data.from_ints(IntsSequence(get_balance_call.result.res, get_balance_call.result.res_bytes_len))
    
    assert result.to_hex() == trie_proofs[2]['storageProof'][0]['value']

@pytest.mark.asyncio
async def test_get_storage_uint(registry_initialized):
    starknet, facts_registry, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = registry_initialized

    account_proof = list(map(lambda element: Data.from_hex(element).to_ints(), trie_proofs[2]['accountProof']))
    flat_account_proof = []
    flat_account_proof_sizes_bytes = []
    flat_account_proof_sizes_words = []
    for proof_element in account_proof:
        flat_account_proof += proof_element.values
        flat_account_proof_sizes_bytes += [proof_element.length]
        flat_account_proof_sizes_words += [len(proof_element.values)]

    options_set = 15 # saves everything in state

    l1_account_address = Data.from_hex(trie_proofs[1]['address'])
    account_words64 = l1_account_address.to_ints()

    tx = await signer.send_transaction(
        account,
        facts_registry.contract_address,
        "prove_account",
        [
            options_set,
            mocked_blocks[3]['number'],
            account_words64.values[0],
            account_words64.values[1],
            account_words64.values[2],
            len(flat_account_proof_sizes_bytes)] +
            flat_account_proof_sizes_bytes +
            [len(flat_account_proof_sizes_words)] +
            flat_account_proof_sizes_words +
            [len(flat_account_proof)] +
            flat_account_proof)

    print(f"Prove account, execution number of steps: {tx.call_info.cairo_usage.n_steps}")

    slot = Data.from_hex(trie_proofs[2]['storageProof'][0]['key']).to_ints()

    storage_proof = list(map(lambda element: Data.from_hex(element).to_ints(), trie_proofs[2]['storageProof'][0]['proof']))
    flat_storage_proof = []
    flat_storage_proof_sizes_bytes = []
    flat_storage_proof_sizes_words = []
    for proof_element in storage_proof:
        flat_storage_proof += proof_element.values
        flat_storage_proof_sizes_bytes += [proof_element.length]
        flat_storage_proof_sizes_words += [len(proof_element.values)]

    get_balance_call = await facts_registry.get_storage_uint(
        mocked_blocks[3]['number'],
        int(trie_proofs[2]['address'][2:], 16),
        tuple(slot.values),
        flat_storage_proof_sizes_bytes,
        flat_storage_proof_sizes_words,
        flat_storage_proof).call()

    print(f"Get balance call n_steps: {get_balance_call.call_info.cairo_usage.n_steps}")
    

