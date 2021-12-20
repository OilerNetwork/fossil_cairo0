from brownie import accounts
from itertools import chain
from collections import Counter

from utils.helpers import hex_string_to_words64, word64_to_nibbles, hex_string_to_nibbles, words64_to_nibbles
from utils.nibbles import merkle_patricia_input_decode
from mocks.trie_proofs import trie_proofs

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

# TODO test decode nibbles with skip_nibbles > 0

def test_merkle_patricia_decode_leaf(TestTrieProofs):
    account_proof = trie_proofs[0]['accountProof']
    leaf_node = account_proof[len(account_proof) - 1]

    test_trie_proofs = accounts[0].deploy(TestTrieProofs)

    expected_output = str(test_trie_proofs.merklePatriciaCompactDecode(leaf_node))
    output = merkle_patricia_input_decode(hex_string_to_words64(leaf_node), len(leaf_node) - 2)

    assert Counter(output) == Counter(hex_string_to_nibbles(expected_output))

