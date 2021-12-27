from typing import List, Tuple
from utils.rlp import isRlpList

from utils.helpers import hex_string_to_words64, keccak_words64, words64_to_nibbles, word64_to_nibbles
from utils.rlp import extractData, to_list, RLPItem


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
    """Checks the path nibbles VS node_path nibbles
    
    Parameters:
    path_offset (int): Offset of already verified nibbles (in nibbles)
    path (List[int]): A path to verify as a list nibbles (64 nibbles)
    path_len (int): A length of path (in nibbles = 64)
    node_path (List[int]): A node_path to check against path as a list of nibbles
    node_path_len (int): A length of node_path (in nibbles)
    current_index: (int): Used for recursion - a current nibble index

    Returns:
    (int): An offsett of path until which the nibbles are the same (should be added to existing path_offset)
    """
    if current_index + path_offset >= path_len and current_index >= node_path_len:
        return current_index
    else:
        if path[current_index + path_offset] != node_path[current_index]:
            return current_index
        else:
            return count_shared_prefix_len(path_offset, path, path_len, node_path, node_path_len, current_index + 1)


def extract_nibble(words: List[int], input_len_bytes: int, position: int) -> int:
    assert position < input_len_bytes * 2
    (target_word, index) = divmod(position, 16)
    return (words[target_word] >> (4*(15 - index))) & 0xF


def get_next_hash(rlp: List[int], node: RLPItem) -> List[int]:
    assert node.length == 32
    res = extractData(rlp, node.dataPosition, 32)
    assert len(res) == 4
    return res


# TODO check if 64 should be replaced with len(path)
def verify_proof(
    path: List[int],
    root_hash: List[int],
    proof: List[List[int]],
    proof_lens: List[int]
) -> Tuple[List[int], int]:
    """Verifies the correctness of a merkle-patricia proof
    
    Parameters:
    path (List[int]): path(account for account proof, slot for storage proof) provided as a list of int words. 32bytes (64 nibbles)
    root_hash (List[int]): keccak256 root of the tree. 32 bytes provided as 4 64bit big endian words.
    proof (List[List[int]]): Result of eth_getProof for either account or storage where each element of the proof is encoded to 64bit words encoded to big endian.
    proof_lens (List[int]): Proof elements lengths

    Returns:
    List[int]: Big endian encoded value of the merkle patricia tree node matching the provided arguments.
    int: size of the key
    """
    assert len(proof) == len(proof_lens)

    if len(proof) == 0:
        assert root_hash == hex_string_to_words64(EMPTY_TRIE_ROOT_HASH)
        return ([], 0)

    next_hash = []
    path_offset = 0

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
            node_path = merkle_patricia_input_decode(extractData(element, node[0].dataPosition, node[0].length), node[0].length)
            path_offset += count_shared_prefix_len(path_offset, words64_to_nibbles(path, 32), 64, node_path, len(node_path))
            if i == len(proof) - 1:
                assert path_offset == 64 # Unexpected end of proof (leaf)
                return (extractData(element, node[1].dataPosition, node[1].length), node[1].length)
            else:
                children = node[1]
                if not isRlpList(element, children.dataPosition):
                    next_hash = get_next_hash(element, children)
                else:
                    next_hash = keccak_words64(extractData(element, children.dataPosition, children.length), children.length)
        else:
            assert len(node) == 17

            if i == element_len - 1:
                if path_offset + 1 == 64:
                    return (extractData(element, node[16].dataPosition, node[16].length), node[16].length)
                else:
                    node_children = extract_nibble(path, 32, path_offset)
                    children = node[node_children]
                    assert len(extractData(element, children.dataPosition, children.length)) == 0
                    return ([], 0)
            else:
                assert path_offset < 64
                node_children = extract_nibble(path, 32, path_offset)
                children = node[node_children]

                path_offset += 1

                if not isRlpList(element, children.dataPosition):
                    next_hash = get_next_hash(element, children)
                else:
                    next_hash = keccak_words64(element, children.length)
    assert False


                
            
        
