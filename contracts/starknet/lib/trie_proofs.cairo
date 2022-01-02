from starkware.cairo.common.cairo_builtins import BitwiseBuiltin
from starkware.cairo.common.math_cmp import is_le

from starknet.lib.extract_from_rlp import IntsSequence, RLPItem, extractData
from starknet.lib.words64 import extract_nibble, extract_nibble_from_words

from starknet.types import Keccak256Hash


func count_shared_prefix_len{ range_check_ptr, bitwise_ptr : BitwiseBuiltin* }(
    path_offset: felt,
    path: IntsSequence,
    proof_element: IntsSequence,
    leading_leaf_node_rlp_item: RLPItem) -> (new_path_offset: felt):
    alloc_locals

    let (local node_path_decoded: IntsSequence) = extractData(proof_element.element, proof_element.element_size_words, leading_leaf_node_rlp_item.length)

    # TODO assert input_decoded len > 0

    # Extract node_path
    # Assumption that the first word of the proof element will be always a full word(8 bytes)
    let (first_nibble) = extract_nibble(node_path_decoded.element[0], 8, 0)

    local skip_nibbles

    if first_nibble == 0:
        skip_nibbles = 2
    else:
        if first_nibble == 1:
            skip_nibbles = 1
        else:
            if first_nibble == 2:
                skip_nibbles = 2
            else:
                if first_nibble == 3:
                    skip_nibbles = 1
                else:
                    assert 1 = 0
                end
            end
        end
    end

    let (shared_prefix) = count_shared_prefix_len_rec(path_offset, path, proof_element, skip_nibbles, 0)
    return (shared_prefix + path_offset)
end

func count_shared_prefix_len_rec{ range_check_ptr, bitwise_ptr : BitwiseBuiltin* }(
    path_offset: felt,
    path: IntsSequence,
    proof_element: IntsSequence,
    skip_nibbles: felt,
    current_index: felt) -> (res: felt):
    let node_path_nibbles_len = proof_element.element_size_bytes * 2 - skip_nibbles
    let path_nibbles_len = path.element_size_bytes * 2

    # current_index + path_offset >= len(path)
    let (path_completed) = is_le(path_nibbles_len, current_index + path_offset)
    # current_index >= len(node_path)
    let (node_path_completed) = is_le(node_path_nibbles_len, current_index)

    if path_completed + node_path_completed == 2:
        return (current_index)
    end

    let (current_path_nibble) = extract_nibble_from_words(path, current_index + path_offset)
    let (current_node_path_nibble) = extract_nibble_from_words(proof_element, current_index + skip_nibbles)

    if current_path_nibble == current_node_path_nibble:
        return count_shared_prefix_len_rec(path_offset, path, proof_element, skip_nibbles, current_index + 1)
    else:
        return (current_index)
    end
end

func get_next_hash{ range_check_ptr, bitwise_ptr : BitwiseBuiltin* }(rlp_input: IntsSequence, rlp_node: RLPItem) -> (res: Keccak256Hash):
    alloc_locals
    assert rlp_node.length == 32
    let (local res: IntsSequence) = extractData(rlp, node.dataPosition, 32)
    assert res.element_size_words == 4
    return Keccak256Hash(res.element[0], res.element[1], res.element[2], res.element[3])
end