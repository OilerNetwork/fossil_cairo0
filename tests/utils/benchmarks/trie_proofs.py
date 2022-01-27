from typing import List

from utils.helpers import hex_string_to_words64, keccak_words64, words64_to_nibbles, words64_to_nibbles, IntsSequence
from utils.rlp import extractData, to_list, RLPItem, isRlpList_RlpItem


EMPTY_TRIE_ROOT_HASH = "0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421"


def merkle_patricia_input_decode(input: IntsSequence) -> List[int]:
    first_nibble = words64_to_nibbles(input)[0]

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

    if skip_nibbles >= input.length:
        return []
    return words64_to_nibbles(input, skip_nibbles)


def count_shared_prefix_len(
    current_path_offset: int,
    path: List[int],
    node_path: List[int],
    current_index: int = 0
) -> int:
    """Checks the path nibbles VS node_path nibbles
    
    Parameters:
    current_path_offset (int): Offset of already verified nibbles (in nibbles)
    path (List[int]): A path to verify as a list nibbles (64 nibbles)
    node_path (List[int]): A node_path to check against path as a list of nibbles
    current_index: (int): Used for recursion - a current nibble index

    Returns:
    (int): An offsett of path until which the nibbles are the same (should be added to existing path_offset)
    """
    if current_index + current_path_offset >= len(path) and current_index >= len(node_path):
        return current_index
    else:
        if path[current_index + current_path_offset] != node_path[current_index]:
            return current_index
        else:
            return count_shared_prefix_len(current_path_offset, path, node_path, current_index + 1)


def extract_nibble(input: IntsSequence, position: int) -> int:
    assert position < input.length * 2
    (target_word, index) = divmod(position, 16)
    word_size_bytes = 8 if target_word < len(input.values) -1 else input.length % 8
    word_size_bytes = 8 if word_size_bytes == 0 else word_size_bytes
    return (input.values[target_word] >> (4*(word_size_bytes * 2 - 1 - index))) & 0xF


def get_next_hash(rlp: IntsSequence, node: RLPItem) -> IntsSequence:
    assert node.length == 32
    res = extractData(rlp, node.dataPosition, 32)
    assert len(res.values) == 4
    return res


def verify_proof(
    path: IntsSequence,
    root_hash: IntsSequence,
    proof: List[IntsSequence]
) -> IntsSequence:
    """Verifies the correctness of a merkle-patricia proof
    
    Parameters:
    path (IntsSequence): path(account for account proof, slot for storage proof) provided as a list of int words. 32bytes (64 nibbles)
    root_hash (IntsSequence): keccak256 root of the tree. 32 bytes provided as 4 64bit big endian words.
    proof (List[IntsSequence]): Result of eth_getProof for either account or storage where each element of the proof is encoded to 64bit words encoded to big endian.

    Returns:
    IntsSequence: Big endian encoded value of the merkle patricia tree node matching the provided arguments.
    """

    if len(proof) == 0:
        assert root_hash == hex_string_to_words64(EMPTY_TRIE_ROOT_HASH)
        return IntsSequence([], 0)

    next_hash = IntsSequence([], 0)
    path_offset = 0

    for i in range(0, len(proof)):
        element_rlp = proof[i]

        if i == 0:
            assert root_hash == keccak_words64(element_rlp)
        else:
            if next_hash != keccak_words64(element_rlp):
                assert next_hash == keccak_words64(element_rlp)

        node = to_list(element_rlp)

        # Handle leaf node
        if len(node) == 2:
            node_path = merkle_patricia_input_decode(extractData(element_rlp, node[0].dataPosition, node[0].length))
            path_offset += count_shared_prefix_len(path_offset, words64_to_nibbles(path), node_path)
            if i == len(proof) - 1:
                assert path_offset == path.length*2 # Unexpected end of proof (leaf)
                return extractData(element_rlp, node[1].dataPosition, node[1].length)
            else:
                children = node[1]
                if not isRlpList_RlpItem(element_rlp, children):
                    next_hash = get_next_hash(element_rlp, children)
                else:
                    next_hash = keccak_words64(extractData(element_rlp, children.dataPosition, children.length))
        else:
            assert len(node) == 17

            if i == len(proof) - 1:
                if path_offset + 1 == path.length*2:
                    return extractData(element_rlp, node[16].dataPosition, node[16].length)
                else:
                    node_children = extract_nibble(path, path_offset)
                    children = node[node_children]
                    assert children.length == 0
                    return IntsSequence([], 0)
            else:
                assert path_offset < path.length*2
                node_children = extract_nibble(path, path_offset)
                children = node[node_children]

                path_offset += 1

                if not isRlpList_RlpItem(element_rlp, children):
                    next_hash = get_next_hash(element_rlp, children)
                else:
                    next_hash = keccak_words64(extractData(element_rlp, children.dataPosition, children.length))
    assert False
