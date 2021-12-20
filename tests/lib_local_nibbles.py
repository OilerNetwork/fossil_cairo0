from brownie import accounts
from itertools import chain
from collections import Counter

from utils.helpers import (
    hex_string_to_words64,
    word64_to_nibbles,
    hex_string_to_nibbles,
    words64_to_nibbles,
    print_ints_array
)
from utils.nibbles import merkle_patricia_input_decode
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
    
    output = words64_to_nibbles(words64, (len(input) - 2), 1)
    expected_output_hex = str(test_trie_proofs.decodeNibbles(input, 1))
    expected_output = hex_string_to_nibbles(expected_output_hex)

    assert output[0:16] == expected_output[0:16]


def test_word64_to_nibbles_skip_2(TestTrieProofs):
    test_trie_proofs = accounts[0].deploy(TestTrieProofs)

    input = '0x338cfc997a82252167ac25a16580d9730353eb1b9f0c6bbf0e4c82c4d0'
    words64 = hex_string_to_words64(input)
    
    output = words64_to_nibbles(words64, (len(input) - 2), 2)
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
    output = words64_to_nibbles(hex_string_to_words64(extension_node), len(extension_node) - 2)

    assert Counter(output) == Counter(hex_string_to_nibbles(expected_output))


def test_decode_nibbles_branch_node(TestTrieProofs):
    account_proof = trie_proofs[0]['accountProof']
    branch_node = account_proof[0]

    test_trie_proofs = accounts[0].deploy(TestTrieProofs)

    expected_output = str(test_trie_proofs.decodeNibbles(branch_node, 0))
    output = words64_to_nibbles(hex_string_to_words64(branch_node), len(branch_node) - 2)

    assert Counter(output) == Counter(hex_string_to_nibbles(expected_output))


def test_merkle_patricia_decode_leaf(TestTrieProofs):
    test_trie_proofs = accounts[0].deploy(TestTrieProofs)
    account_proof = trie_proofs[0]['accountProof']
    leaf_node = account_proof[len(account_proof) - 1]
    leaf_node_64 = hex_string_to_words64(leaf_node)

    leaf_node_items = to_list(leaf_node_64)
    leaf_node_values = extract_list_values(leaf_node_64, leaf_node_items)

    leaf_node_value = '0x338cfc997a82252167ac25a16580d9730353eb1b9f0c6bbf0e4c82c4d0'

    output = merkle_patricia_input_decode(leaf_node_values[0], len(leaf_node_value) - 2)
    expected_output = str(test_trie_proofs.merklePatriciaCompactDecode(leaf_node_value))

    assert Counter(output) == Counter(hex_string_to_nibbles(expected_output))

