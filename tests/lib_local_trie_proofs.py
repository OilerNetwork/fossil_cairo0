import pytest
from brownie import accounts
from utils.encode_proof import encode_proof
from web3 import Web3

from rlp import decode, encode

from utils.types import Data

from utils.helpers import (
    hex_string_to_words64,
    words64_to_nibbles,
    keccak_words64
)
from utils.benchmarks.trie_proofs import merkle_patricia_input_decode, verify_proof, count_shared_prefix_len, extract_nibble
from mocks.trie_proofs import trie_proofs, transaction_proofs, receipts_proofs
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

def test_verify_valid_storage_proof_non_zero_value(TestTrieProofs):
    test_trie_proofs = accounts[0].deploy(TestTrieProofs)

    account_state_root = Data.from_hex('0x199c2e6b850bcc9beaea25bf1bacc5741a7aad954d28af9b23f4b53f5404937b')
    proof = Data.from_hex(encode_proof(trie_proofs[2]['storageProof'][0]['proof']))
    proof_path = Data.from_hex(Web3.keccak(hexstr=trie_proofs[2]['storageProof'][0]['key']).hex())

    expected_value = Data.from_hex(str(test_trie_proofs.verify(proof.to_bytes(), account_state_root.to_bytes(), proof_path.to_bytes(), {"from": accounts[0]})))

    proof_to_ints = list(map(lambda element: Data.from_hex(element).to_ints(), trie_proofs[2]['storageProof'][0]['proof']))
    value = Data.from_ints(verify_proof(
        proof_path.to_ints(),
        account_state_root.to_ints(),
        proof_to_ints
    ))

    assert value == expected_value


def test_verify_valid_transaction_proof(TestTrieProofs):
    test_trie_proofs = accounts[0].deploy(TestTrieProofs)

    transactions_root = Data.from_hex('0x51ed72794eb419a76b9844d476e0359b35d8a26418b0b914aca89d22c4c993ce') #Data.from_hex('0x51a8f471a6eed8d7da6aa588eb4e9a0764770f5c20b0e1e05c1210abbb05dd78')
    proof_path = Data.from_hex("0x" + encode(Data.from_hex('0xd6').to_bytes()).hex()) #Data.from_hex("0x" + encode(Data.from_hex(transaction_proofs[0]['transaction']['transactionIndex']).to_bytes()).hex())

    proof_tmp = [
            "0xf90131a0d62d3fc2e5c08cf7bded97ff07ba068a4828a9a178c6605d86b8dec5d2b6b90ba02d63ec096b76779d230031c73b8d0861d29a99219f094b464de9a216330a440ea0a9c6633035286f212d0f4467d1504f4d35f9aa03af314aa58d5e0d70e9d430b9a03b36f2a540cacee898bcf0f66ccb7092a069aa97cb50cec3d362c717df77fb9fa0c45a7698a190ee92900887a4529b082b851ae037a6efc2a680986a41dc986df8a00846e3dc4778171caad61941f56a1eb4d65ef983cd4770b6f02c84040e3342a9a05746431d64aa462227e18abf0cc0d07b191d18b729ffae3ff90bbca7b75769aca07c7134f9bff844e23db5023bcc231ac89f03f6974e7203c1428e0dd5012d4995a01028c0cd59945b56ab779f11f7ce7dc2451b547bd459a5e66deeb79d5c7b07548080808080808080",
            "0xf851a0cc45cf7bb6525b6c75a1674d8bc0c6f264f373dbde3119e97257b83f7663a4c1a046edd7cf45005e488a283e44efeed92605c402dd77c045f1d7ca47a48d86f8f1808080808080808080808080808080",
            "0xf8d18080808080808080a054e41a1c7de04bc81ffdc58f94e44ae7169763a88f46c5979da51b135b508a77a08f063c0ee7febcdd447df438b2ff67be025cf056be5a17ffa39d83a8030b7e54a09bb15466ed8767b80df0c4875dba4c25d9c36edd9365691afa6d097f28b2ce10a0a1881e5372dd5c8b2b67fcd58ea214a3e27e355b1a46e3d5f32993b0e531b849a04583c8efd6f1f02050236445eaaf51bbf7427f0d63119ae2a92799b4eae7bdc8a05c235315c8a3a1df1f9baa9c6028e241659433132499b493cf799151bd52a0a1808080",
            "0xf901b1a0cf506b7034b9ff7108eb66e88185580358e544947a64bc8f8830b6696eda24eca0812bb72d8c9efbb611b1fdafbffc72bfd0e57d421618f305387c7c58217e0ee3a01a5c5109ede392ad5bab92f9de1c60851e4c3c165bc7ec992d5df99105046412a02397581556423644d196d053bd948fc3df4ed930323e729939a0fc612b6acabaa03612a21f982681abf00b4961c494f24acc64b256abb0b0270d2703523aa31d9ba0ec67a68c75a7f7e645f492f58d17dca8f90b153c8597480371824e9881575850a05c953120d072b51fe3ea708e9cd68f6fb2b67948d8fbc5a6bd81cb8fc8f7797ea09def0c596656c091226685ec7be432c4612a98f276ee3f3e3ce8e23193427167a08270fbb248a27212d96769fa3ff3990bf0e8fe12d2d83d694fbf59846a1a6c61a02faed51a938b7bbdcaab4977a4b4ba83f1479cf241b8c0e694d2af94eeaa2e8ca0cbe3425a6eca41c21b1a5c28453de6f9eca7ed5e95275063912841e5ab267f35a04f4d75a8b77c0cc5accd65c3c0ec99aaa130355d09b10c419d25e6a00818fc3ba0cf3560d7b2ae6163cc59f9134ba7380ee76d62c94b770e000c28138b7c2a6eef80808080",
            "0xf87420b871f86f8305cedb851dfd14080082c350944f06abd6adb193039dab57813259dcd10f4aaf078803fec0aac4ded9f5801ba09541fd959703f023e3d752d2af2493c66a7bf0786ba1686a710a7002021ec57fa01e34fc246b4682ecfc2a091f3242e8ccbad4b3926c9d5ff64ce89ddd3d368e59"
        ]

    proof_to_ints = list(map(lambda element: Data.from_hex(element).to_ints(), proof_tmp)) # list(map(lambda element: Data.from_hex(element).to_ints(), transaction_proofs[0]['txProof']))
    value = Data.from_ints(verify_proof(
        proof_path.to_ints(),
        transactions_root.to_ints(),
        proof_to_ints
    ))

    print(value)

def test_verify_valid_receipt_proof(TestTrieProofs):
    test_trie_proofs = accounts[0].deploy(TestTrieProofs)

    receipts_root = Data.from_hex('0xbd470fa25c3b2c1c746a8f220a0c351882eb64b358357a7fde8dd77f327f0240')
    proof = Data.from_hex(encode_proof(receipts_proofs[0]['receiptProof']))
    proof_path = Data.from_hex("0x" + encode(Data.from_hex(receipts_proofs[0]['receipt']['transactionIndex']).to_bytes()).hex())

    proof_to_ints = list(map(lambda element: Data.from_hex(element).to_ints(), receipts_proofs[0]['receiptProof']))
    value = Data.from_ints(verify_proof(
        proof_path.to_ints(),
        receipts_root.to_ints(),
        proof_to_ints
    ))

    print(value)
    # assert value == expected_value
    
