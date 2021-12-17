from typing import List, Callable, NamedTuple
from web3 import Web3

from utils.helpers import rlp_string_to_words64, ints_array_to_bytes, keccak_words64
from utils.rlp import extractData, getElement, isRlpList



class LeafeNode(NamedTuple):
    key: List[int]
    value: List[int]

class BranchNode(NamedTuple):
    nib_0: LeafeNode
    nib_1: LeafeNode
    nib_2: LeafeNode

EMPTY_TRIE_ROOT_HASH = "0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421"

def decode_nibbles(input: List[int], skip_nibbles: int = 0) -> List[int]:
    if len(input) == 0: raise Exception("Empty input")

    input_byte_chunked: List[int] = []
    for i in range(0, len(input)):
        word_bytes: List[int] = []
        for j in range(7, 0, -1):
            word_bytes.append(input_byte_chunked[i] >> 8*j)
        input_byte_chunked.extend(word_bytes)

    length = len(input) * 8 * 2
    if skip_nibbles > length: raise Exception("Skip nibbles to large")
    length -= skip_nibbles

    nibbles: List[int] = []

    for i in range(skip_nibbles, skip_nibbles + length):
        (_, r) = divmod(i, 2)
        if r == 0:
           nibbles.append()

def verify_account_proof(
    account: List[int],
    root_hash: List[int],
    proof: List[List[int]],
    proof_lens: List[int]
) -> List[int]:
    assert len(proof) == len(proof_lens)

    if len(proof) == 0:
        assert root_hash == rlp_string_to_words64(EMPTY_TRIE_ROOT_HASH)
        return []

    next_hash = []

    for i in range(0, len(proof)):
        element = proof[i]
        element_len = proof_lens[i]

        if i == 0:
            assert root_hash == keccak_words64(element, element_len)
        else:
            assert next_hash == keccak_words64(element, element_len)
        

    
    
