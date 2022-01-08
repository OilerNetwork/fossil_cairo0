import pytest
import asyncio
from typing import NamedTuple

from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.testing.starknet import Starknet

from mocks.trie_proofs import trie_proofs
from utils.helpers import IntsSequence
from utils.types import Data
from utils.rlp import to_list, extract_list_values

from web3 import Web3

from utils.benchmarks.trie_proofs import (
    count_shared_prefix_len,
    merkle_patricia_input_decode,
    get_next_hash,
    verify_proof,
    RLPItem)


class TestsDeps(NamedTuple):
    starknet: Starknet
    trie_proofs_contract: StarknetContract

@pytest.fixture(scope='module')
def event_loop():
    return asyncio.new_event_loop()

async def setup():
    starknet = await Starknet.empty()
    trie_proofs_contract = await starknet.deploy(source="contracts/starknet/test/TestTrieProofs.cairo", cairo_path=["contracts"])
    return TestsDeps(
        starknet=starknet,
        trie_proofs_contract=trie_proofs_contract
    )

@pytest.fixture(scope='module')
async def factory():
    return await setup()


@pytest.mark.asyncio
async def test_count_shared_prefix_len(factory):
    starknet, trie_proofs_contract = factory

    # Inputs
    proof = trie_proofs[1]['accountProof']
    element_rlp = Data.from_hex(proof[len(proof) - 1])

    path = Data.from_hex(Web3.keccak(hexstr=trie_proofs[1]['address']).hex())
    path_offset = 7

    # Get expected values
    node_path_items = to_list(element_rlp.to_ints().values)
    node_path_items_extracted = extract_list_values(element_rlp.to_ints(), node_path_items)
    node_path_nibbles = merkle_patricia_input_decode(node_path_items_extracted[0])
    expected_shared_prefix = path_offset + count_shared_prefix_len(path_offset, path.to_nibbles(), node_path_nibbles)

    # Invoke test
    count_shared_prefix_len_call = await trie_proofs_contract.test_count_shared_prefix_len(
        path_offset,
        path.to_ints().values,
        path.to_ints().length,
        element_rlp.to_ints().values,
        element_rlp.to_ints().length,
        node_path_items[0].dataPosition,
        node_path_items[0].length).call()

    assert count_shared_prefix_len_call.result.res == expected_shared_prefix


@pytest.mark.asyncio
async def test_get_next_element_hash(factory):
    starknet, trie_proofs_contract = factory

    print(
        Data.from_hex('0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421').to_ints()
    )

    # Inputs
    proof = trie_proofs[1]['accountProof']
    element_rlp = Data.from_hex(proof[len(proof) - 2])
    rlp_item = RLPItem(dataPosition=173, length=32)

    expected_result = get_next_hash(element_rlp.to_ints(), rlp_item)

    get_next_hash_call = await trie_proofs_contract.test_get_next_hash(
        element_rlp.to_ints().values,
        element_rlp.to_ints().length,
        rlp_item.dataPosition,
        rlp_item.length
    ).call()

    result = get_next_hash_call.result.res

    assert Data.from_ints(IntsSequence(result, 32)) == Data.from_ints(expected_result)


@pytest.mark.asyncio
async def test_verify_valid_account_proof(factory):
    starknet, trie_proofs_contract = factory

    block_state_root = Data.from_hex('0x2045bf4ea5561e88a4d0d9afbc316354e49fe892ac7e961a5e68f1f4b9561152')
    proof_path = Data.from_hex(Web3.keccak(hexstr=trie_proofs[1]['address']).hex())
    proof = list(map(lambda element: Data.from_hex(element).to_ints(), trie_proofs[1]['accountProof']))

    # Python implementation as a reference
    expected_key = Data.from_ints(verify_proof(
        proof_path.to_ints(),
        block_state_root.to_ints(),
        proof)
    )

    flat_proof = []
    flat_proof_sizes_bytes = []
    flat_proof_sizes_words = []

    for proof_element in proof:
        flat_proof += proof_element.values
        flat_proof_sizes_bytes += [proof_element.length]
        flat_proof_sizes_words += [len(proof_element.values)]

    verify_proof_call = await trie_proofs_contract.test_verify_proof(
        proof_path.to_ints().length,
        proof_path.to_ints().values,
        block_state_root.to_ints().length,
        block_state_root.to_ints().values,
        flat_proof_sizes_bytes,
        flat_proof_sizes_words,
        flat_proof
    ).call()

    result = Data.from_ints(IntsSequence(verify_proof_call.result.res, verify_proof_call.result.res_size_bytes))

    print("\n\n\nResulting proofs:\n\n")

    print("Python:", expected_key.to_hex())

    print(" Cairo:", result.to_hex())

    assert result == expected_key
