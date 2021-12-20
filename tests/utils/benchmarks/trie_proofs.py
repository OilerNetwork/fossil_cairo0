from typing import List, Callable, NamedTuple
from web3 import Web3

from utils.helpers import hex_string_to_words64, ints_array_to_bytes, keccak_words64
from utils.rlp import extractData, getElement, to_list


class LeafeNode(NamedTuple):
    key: List[int]
    value: List[int]

class BranchNode(NamedTuple):
    nib_0: LeafeNode
    nib_1: LeafeNode
    nib_2: LeafeNode

EMPTY_TRIE_ROOT_HASH = "0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421"

def verify_account_proof(
    account: List[int],
    root_hash: List[int],
    proof: List[List[int]],
    proof_lens: List[int]
) -> List[int]:
    assert len(proof) == len(proof_lens)

    if len(proof) == 0:
        assert root_hash == hex_string_to_words64(EMPTY_TRIE_ROOT_HASH)
        return []

    next_hash = []

    for i in range(0, len(proof)):
        element = proof[i]
        element_len = proof_lens[i]

        if i == 0:
            assert root_hash == keccak_words64(element, element_len)
        else:
            assert next_hash == keccak_words64(element, element_len)

        node = to_list(element)

        # Handle leaf node
        if len(node) == 2:
            # TODO wtf is div
        

    
    
