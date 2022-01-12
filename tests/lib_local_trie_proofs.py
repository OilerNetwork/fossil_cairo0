import pytest
from brownie import accounts
from utils.encode_proof import encode_proof
from web3 import Web3

from rlp import decode

from utils.types import Data

from utils.helpers import (
    hex_string_to_words64,
    words64_to_nibbles,
    keccak_words64
)
from utils.benchmarks.trie_proofs import merkle_patricia_input_decode, verify_proof, count_shared_prefix_len, extract_nibble
from mocks.trie_proofs import trie_proofs
from utils.rlp import extract_list_values, to_list


def test_word64_to_nibbles_skip_0(TestTrieProofs):
    test_trie_proofs = accounts[0].deploy(TestTrieProofs)

    input = Data.from_hex('0x338cfc997a82252167ac25a16580d9730353eb1b9f0c6bbf0e4c82c4d0')
    
    output = Data.from_nibbles(words64_to_nibbles(input.to_ints()))
    expected_output_bytes = Data.from_hex(str(test_trie_proofs.decodeNibbles(input.to_hex(), 0))).to_bytes()
    expected_output = Data.from_nibbles(list(expected_output_bytes))

    assert output == expected_output


def test_word64_to_nibbles_skip_1(TestTrieProofs):
    test_trie_proofs = accounts[0].deploy(TestTrieProofs)

    input = Data.from_hex('0x338cfc997a82252167ac25a16580d9730353eb1b9f0c6bbf0e4c82c4d0')
    
    output = Data.from_nibbles(words64_to_nibbles(input.to_ints(), 1))
    expected_output_bytes = Data.from_hex(str(test_trie_proofs.decodeNibbles(input.to_hex(), 1))).to_bytes()
    expected_output = Data.from_nibbles(list(expected_output_bytes))

    assert output == expected_output


def test_word64_to_nibbles_skip_2(TestTrieProofs):
    test_trie_proofs = accounts[0].deploy(TestTrieProofs)

    input = Data.from_hex('0x338cfc997a82252167ac25a16580d9730353eb1b9f0c6bbf0e4c82c4d0')
    
    output = Data.from_nibbles(words64_to_nibbles(input.to_ints(), 2))
    expected_output_bytes = Data.from_hex(str(test_trie_proofs.decodeNibbles(input.to_hex(), 2))).to_bytes()
    expected_output = Data.from_nibbles(list(expected_output_bytes))

    assert output == expected_output


def test_decode_nibbles_leaf_node(TestTrieProofs):
    account_proof = trie_proofs[0]['accountProof']
    leaf_node = account_proof[len(account_proof) - 1]

    test_trie_proofs = accounts[0].deploy(TestTrieProofs)

    expected_output_bytes = Data.from_hex(str(test_trie_proofs.decodeNibbles(leaf_node, 0))).to_bytes()
    expected_output = Data.from_nibbles(list(expected_output_bytes))

    output = Data.from_nibbles(words64_to_nibbles(Data.from_hex(leaf_node).to_ints()))

    assert output == expected_output


def test_decode_nibbles_extension_node(TestTrieProofs):
    account_proof = trie_proofs[0]['accountProof']
    extension_node = account_proof[len(account_proof) - 2]

    test_trie_proofs = accounts[0].deploy(TestTrieProofs)

    expected_output_bytes = Data.from_hex(str(test_trie_proofs.decodeNibbles(extension_node, 0))).to_bytes()
    expected_output = Data.from_nibbles(list(expected_output_bytes))

    output = Data.from_nibbles(words64_to_nibbles(Data.from_hex(extension_node).to_ints()))

    assert output == expected_output


def test_decode_nibbles_branch_node(TestTrieProofs):
    account_proof = trie_proofs[0]['accountProof']
    branch_node = account_proof[0]

    test_trie_proofs = accounts[0].deploy(TestTrieProofs)

    expected_output_bytes = Data.from_hex(str(test_trie_proofs.decodeNibbles(branch_node, 0))).to_bytes()
    expected_output = Data.from_nibbles(list(expected_output_bytes))
    output = Data.from_nibbles(words64_to_nibbles(Data.from_hex(branch_node).to_ints()))

    assert output == expected_output


def test_merkle_patricia_decode_leaf(TestTrieProofs):
    test_trie_proofs = accounts[0].deploy(TestTrieProofs)
    account_proof = trie_proofs[0]['accountProof']
    leaf_node = Data.from_hex(account_proof[len(account_proof) - 1])

    leaf_node_items = to_list(leaf_node.to_ints())
    leaf_node_values = extract_list_values(leaf_node.to_ints(), leaf_node_items)

    leaf_node_value = decode(leaf_node.to_bytes())[0]

    output = Data.from_nibbles(merkle_patricia_input_decode(leaf_node_values[0]))
    expected_output_bytes = Data.from_hex(str(test_trie_proofs.merklePatriciaCompactDecode(leaf_node_value))).to_bytes()
    expected_output = Data.from_nibbles(list(expected_output_bytes))

    assert output == expected_output


def test_verify_invalid_proof_account_not_hashed():
    account = hex_string_to_words64('0x78e05971af7857d6114f7f896f9fd58d5c5d18e5')
    root_hash = hex_string_to_words64('0x96c4bdfb8f2ad089200bad93f6216fe96652f9e2761b55bfd8a715ad3d6ecaf6')
    node = trie_proofs[0]['storageProof'][0]['proof'][0]
    proof = [hex_string_to_words64(node)]
    proof_lens = [int((len(node) - 2) / 2)]
    with pytest.raises(Exception):
        verify_proof(account, root_hash, proof, proof_lens)


def test_verify_invalid_proof_invalid_path():
    account = keccak_words64(Data.from_hex('0x78e05971af7857d6114f7f896f9fd58d5c5d18e5').to_ints())
    root_hash = hex_string_to_words64('0x96c4bdfb8f2ad089200bad93f6216fe96652f9e2761b55bfd8a715ad3d6ecaf6')
    node = trie_proofs[0]['storageProof'][0]['proof'][0]
    proof = [hex_string_to_words64(node)]
    proof_lens = [int((len(node) - 2) / 2)]
    with pytest.raises(Exception):
        verify_proof(account, root_hash, proof, proof_lens)


def test_count_shared_prefix_len(TestTrieProofs):
    test_trie_proofs = accounts[0].deploy(TestTrieProofs)
    proof = trie_proofs[1]['accountProof']
    leaf_node = Data.from_hex(proof[len(proof) - 1])

    leaf_node_items = to_list(leaf_node.to_ints())
    leaf_node_values = extract_list_values(leaf_node.to_ints(), leaf_node_items)

    leaf_node_value = decode(leaf_node.to_bytes())[0]

    node_path_nibbles = merkle_patricia_input_decode(leaf_node_values[0])
    node_path = test_trie_proofs.merklePatriciaCompactDecode(leaf_node_value)

    path = Data.from_hex('0x2045bf4ea5561e88a4d0d9afbc316354e49fe892ac7e961a5e68f1f4b9561152')

    shared_prefix_expected = test_trie_proofs.sharedPrefixLength(0, path.to_bytes(), node_path)
    shared_prefix = count_shared_prefix_len(0, path.to_nibbles(), node_path_nibbles)

    assert shared_prefix_expected == shared_prefix


def test_extract_nibble(TestTrieProofs):
    test_trie_proofs = accounts[0].deploy(TestTrieProofs)

    input = Data.from_hex('0x199c2e6b850bcc9beaea25bf1bacc5741a7aad954d28af9b23f4b53f5404937b')

    for i in range(0, len(input.to_nibbles())):
        output_expected = test_trie_proofs.extractNibble(input.to_bytes(), i)
        output = extract_nibble(input.to_ints(), i)
        assert output == output_expected


def test_verify_valid_account_proof(TestTrieProofs):
    test_trie_proofs = accounts[0].deploy(TestTrieProofs)

    block_state_root = Data.from_hex('0x2045bf4ea5561e88a4d0d9afbc316354e49fe892ac7e961a5e68f1f4b9561152')
    proof = Data.from_hex(encode_proof(trie_proofs[1]['accountProof']))
    proof_path = Data.from_hex(Web3.keccak(hexstr=trie_proofs[1]['address']).hex())

    expected_key = Data.from_hex(str(test_trie_proofs.verify(proof.to_bytes(), block_state_root.to_bytes(), proof_path.to_bytes(), {"from": accounts[0]})))
    key = Data.from_ints(verify_proof(
        proof_path.to_ints(),
        block_state_root.to_ints(),
        list(map(lambda element: Data.from_hex(element).to_ints(), trie_proofs[1]['accountProof']))
    ))

    assert key == expected_key


def test_verify_valid_storage_proof(TestTrieProofs):
    test_trie_proofs = accounts[0].deploy(TestTrieProofs)

    account_state_root = Data.from_hex('0x199c2e6b850bcc9beaea25bf1bacc5741a7aad954d28af9b23f4b53f5404937b')
    proof = Data.from_hex(encode_proof(trie_proofs[1]['storageProof'][0]['proof']))
    proof_path = Data.from_hex(Web3.keccak(hexstr=trie_proofs[1]['storageProof'][0]['key']).hex())

    expected_value = Data.from_hex(str(test_trie_proofs.verify(proof.to_bytes(), account_state_root.to_bytes(), proof_path.to_bytes(), {"from": accounts[0]})))

    proof_to_ints = list(map(lambda element: Data.from_hex(element).to_ints(), trie_proofs[1]['storageProof'][0]['proof']))
    value = Data.from_ints(verify_proof(
        proof_path.to_ints(),
        account_state_root.to_ints(),
        proof_to_ints
    ))

    assert value == expected_value
    print(value)

    


