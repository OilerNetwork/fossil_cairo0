from typing import List, Callable, NamedTuple
from web3 import Web3

from utils.helpers import hex_string_to_words64, keccak_words64, words64_to_nibbles, word64_to_nibbles
from utils.rlp import extractData, getElement, to_list


EMPTY_TRIE_ROOT_HASH = "0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421"


def merkle_patricia_input_decode(input: List[int], input_len_bytes: int) -> List[int]:
    first_nibble = word64_to_nibbles(input[0], 16)[0]

    skip_nibbles = 0

    if first_nibble == 0:
        skip_nibbles = 2
    elif first_nibble == 1:
        skip_nibbles = 1
    elif first_nibble == 2:
        skip_nibbles = 2
    elif first_nibble == 3:
        skip_nibbles = 1
    else:
        assert False

    return words64_to_nibbles(input, input_len_bytes, skip_nibbles)


def count_shared_prefix_len(
    path_offset: int,
    path: List[int],
    path_len: int,
    node_path: List[int],
    node_path_len: int,
    current_index: int = 0
) -> int:
    if current_index + path_offset >= path_len and current_index >= node_path_len:
        return current_index
    else:
        if path[current_index + path_offset] != node_path[current_index]:
            return current_index
        else:
            return count_shared_prefix_len(path_offset, path, path_len, node_path, node_path_len, current_index + 1)


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
            pass
            # TODO wtf is div
        
