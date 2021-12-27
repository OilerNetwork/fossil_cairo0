import pytest
from brownie import accounts
from itertools import chain
from collections import Counter
from utils.encode_proof import encode_proof
from web3 import Web3

from utils.helpers import (
    hex_string_to_words64,
    word64_to_nibbles,
    hex_string_to_nibbles,
    words64_to_nibbles,
    keccak_words64
)
from utils.benchmarks.trie_proofs import merkle_patricia_input_decode, verify_proof, count_shared_prefix_len, extract_nibble
from mocks.trie_proofs import trie_proofs
from utils.rlp import extract_list_values, to_list


def test_word64_to_nibbles_skip_0(TestTrieProofs):
    test_trie_proofs = accounts[0].deploy(TestTrieProofs)

    input = '0x338cfc997a82252167ac25a16580d9730353eb1b9f0c6bbf0e4c82c4d0'
    word64 = hex_string_to_words64(input)[0]
    
    output = word64_to_nibbles(word64, 16)
    expected_output_hex = str(test_trie_proofs.decodeNibbles(input, 0))
    expected_output = hex_string_to_nibbles(expected_output_hex)
    assert expected_output[0:16] == output[0:16]


def test_word64_to_nibbles_skip_1(TestTrieProofs):
    test_trie_proofs = accounts[0].deploy(TestTrieProofs)

    input = '0x338cfc997a82252167ac25a16580d9730353eb1b9f0c6bbf0e4c82c4d0'
    words64 = hex_string_to_words64(input)
    
    output = words64_to_nibbles(words64, int(len(input)/2) - 1, 1)
    expected_output_hex = str(test_trie_proofs.decodeNibbles(input, 1))
    expected_output = hex_string_to_nibbles(expected_output_hex)

    assert output[0:16] == expected_output[0:16]


def test_word64_to_nibbles_skip_2(TestTrieProofs):
    test_trie_proofs = accounts[0].deploy(TestTrieProofs)

    input = '0x338cfc997a82252167ac25a16580d9730353eb1b9f0c6bbf0e4c82c4d0'
    words64 = hex_string_to_words64(input)
    
    output = words64_to_nibbles(words64, int(len(input)/2) - 1, 2)
    expected_output_hex = str(test_trie_proofs.decodeNibbles(input, 2))
    expected_output = hex_string_to_nibbles(expected_output_hex)

    assert output[0:16] == expected_output[0:16]


def test_decode_nibbles_leaf_node(TestTrieProofs):
    account_proof = trie_proofs[0]['accountProof']
    leaf_node = account_proof[len(account_proof) - 1]

    test_trie_proofs = accounts[0].deploy(TestTrieProofs)

    expected_output = str(test_trie_proofs.decodeNibbles(leaf_node, 0))
    output = list(map(lambda word: word64_to_nibbles(word, 16), hex_string_to_words64(leaf_node)))

    assert Counter(chain.from_iterable(output)) == Counter(hex_string_to_nibbles(expected_output))


def test_decode_nibbles_extension_node(TestTrieProofs):
    account_proof = trie_proofs[0]['accountProof']
    extension_node = account_proof[len(account_proof) - 2]

    test_trie_proofs = accounts[0].deploy(TestTrieProofs)

    expected_output = str(test_trie_proofs.decodeNibbles(extension_node, 0))
    output = words64_to_nibbles(hex_string_to_words64(extension_node), int(len(extension_node) / 2) - 1)

    assert Counter(output) == Counter(hex_string_to_nibbles(expected_output))


def test_decode_nibbles_branch_node(TestTrieProofs):
    account_proof = trie_proofs[0]['accountProof']
    branch_node = account_proof[0]

    test_trie_proofs = accounts[0].deploy(TestTrieProofs)

    expected_output = str(test_trie_proofs.decodeNibbles(branch_node, 0))
    output = words64_to_nibbles(hex_string_to_words64(branch_node), int(len(branch_node)/2) - 1)

    assert Counter(output) == Counter(hex_string_to_nibbles(expected_output))


def test_merkle_patricia_decode_leaf(TestTrieProofs):
    test_trie_proofs = accounts[0].deploy(TestTrieProofs)
    account_proof = trie_proofs[0]['accountProof']
    leaf_node = account_proof[len(account_proof) - 1]
    leaf_node_64 = hex_string_to_words64(leaf_node)

    leaf_node_items = to_list(leaf_node_64)
    leaf_node_values = extract_list_values(leaf_node_64, leaf_node_items)

    leaf_node_value = '0x338cfc997a82252167ac25a16580d9730353eb1b9f0c6bbf0e4c82c4d0'

    output = merkle_patricia_input_decode(leaf_node_values[0], int(len(leaf_node_value)/2) - 1)
    expected_output = str(test_trie_proofs.merklePatriciaCompactDecode(leaf_node_value))

    assert Counter(output) == Counter(hex_string_to_nibbles(expected_output))


def test_verify_invalid_proof_account_not_hashed():
    account = hex_string_to_words64('0x78e05971af7857d6114f7f896f9fd58d5c5d18e5')
    root_hash = hex_string_to_words64('0x96c4bdfb8f2ad089200bad93f6216fe96652f9e2761b55bfd8a715ad3d6ecaf6')
    node = trie_proofs[0]['storageProof'][0]['proof'][0]
    proof = [hex_string_to_words64(node)]
    proof_lens = [int((len(node) - 2) / 2)]
    with pytest.raises(Exception):
        verify_proof(account, root_hash, proof, proof_lens)


def test_verify_invalid_proof_invalid_path():
    account = keccak_words64(hex_string_to_words64('0x78e05971af7857d6114f7f896f9fd58d5c5d18e5'), 20)
    root_hash = hex_string_to_words64('0x96c4bdfb8f2ad089200bad93f6216fe96652f9e2761b55bfd8a715ad3d6ecaf6')
    node = trie_proofs[0]['storageProof'][0]['proof'][0]
    proof = [hex_string_to_words64(node)]
    proof_lens = [int((len(node) - 2) / 2)]
    with pytest.raises(Exception):
        verify_proof(account, root_hash, proof, proof_lens)


def test_count_shared_prefix_len(TestTrieProofs):
    test_trie_proofs = accounts[0].deploy(TestTrieProofs)
    proof = trie_proofs[1]['accountProof']
    leaf_node = proof[len(proof) - 1]
    leaf_node_64 = hex_string_to_words64(leaf_node)

    leaf_node_items = to_list(leaf_node_64)
    leaf_node_values = extract_list_values(leaf_node_64, leaf_node_items)

    leaf_node_value = '0x338cfc997a82252167ac25a16580d9730353eb1b9f0c6bbf0e4c82c4d0'

    node_path_words64 = merkle_patricia_input_decode(leaf_node_values[0], int(len(leaf_node_value)/2) - 1)
    node_path = str(test_trie_proofs.merklePatriciaCompactDecode(leaf_node_value))

    block_state_root = '0x2045bf4ea5561e88a4d0d9afbc316354e49fe892ac7e961a5e68f1f4b9561152'

    shared_prefix_expected = test_trie_proofs.sharedPrefixLength(0, block_state_root, node_path)
    shared_prefix = count_shared_prefix_len(0, hex_string_to_words64(block_state_root), len(block_state_root) - 2, node_path_words64, len(leaf_node_value) - 2)

    assert (shared_prefix_expected) == (shared_prefix)


def test_extract_nibbles(TestTrieProofs):
    test_trie_proofs = accounts[0].deploy(TestTrieProofs)

    input = '0x199c2e6b850bcc9beaea25bf1bacc5741a7aad954d28af9b23f4b53f5404937b'

    for i in range(0, 64):
        output_expected = test_trie_proofs.extractNibble(bytes.fromhex(input[2:]), i)
        output = extract_nibble(hex_string_to_words64(input), 32, i)
        assert output == output_expected


def test_verify_valid_account_proof(TestTrieProofs):
    test_trie_proofs = accounts[0].deploy(TestTrieProofs)

    block_state_root = '0x2045bf4ea5561e88a4d0d9afbc316354e49fe892ac7e961a5e68f1f4b9561152'
    proof = encode_proof(trie_proofs[1]['accountProof'])
    proof_path = Web3.keccak(hexstr=trie_proofs[1]['address']).hex()

    test_trie_proofs.verify(proof, block_state_root, proof_path, {"from": accounts[0]})

    proof_words64 = list(map(lambda element: hex_string_to_words64(element), trie_proofs[1]['accountProof']))
    key = verify_proof(
        hex_string_to_words64(proof_path),
        hex_string_to_words64(block_state_root),
        proof_words64,
        list(map(lambda element: int((len(element) / 2) - 1), trie_proofs[1]['accountProof']))
    )

