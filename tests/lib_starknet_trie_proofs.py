import pytest
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
    RLPItem)


class TestsDeps(NamedTuple):
    starknet: Starknet
    trie_proofs_contract: StarknetContract


async def setup():
    starknet = await Starknet.empty()
    trie_proofs_contract = await starknet.deploy(source="contracts/starknet/test/TestTrieProofs.cairo", cairo_path=["contracts"])
    return TestsDeps(
        starknet=starknet,
        trie_proofs_contract=trie_proofs_contract
    )


@pytest.mark.asyncio
async def test_count_shared_prefix_len():
    starknet, trie_proofs_contract = await setup()

    # Inputs
    proof = trie_proofs[1]['accountProof']
    element_rlp = Data.from_hex(proof[len(proof) - 1])

    path = Data.from_hex(Web3.keccak(hexstr=trie_proofs[1]['address']).hex())
    path_offset = 7

    # Get expected values
    node_path_items = to_list(element_rlp.to_ints().values)
    node_path_items_extracted = extract_list_values(element_rlp.to_ints().values, node_path_items)
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
async def test_get_next_element_hash():
    starknet, trie_proofs_contract = await setup()

    print(
        Data.from_hex('0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421').to_ints()
    )

    # Inputs
    proof = trie_proofs[1]['accountProof']
    element_rlp = Data.from_hex(proof[len(proof) - 2])
    rlp_item = RLPItem(dataPosition=173, length=32)

    expected_result = get_next_hash(element_rlp.to_ints().values, rlp_item)

    get_next_hash_call = await trie_proofs_contract.test_get_next_hash(
        element_rlp.to_ints().values,
        element_rlp.to_ints().length,
        rlp_item.dataPosition,
        rlp_item.length
    ).call()

    result = get_next_hash_call.result.res

    assert Data.from_ints(IntsSequence(result, 32)) == Data.from_ints(expected_result)


