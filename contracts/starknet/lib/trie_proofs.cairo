from starkware.cairo.common.cairo_builtins import BitwiseBuiltin

from starknet.lib.extract_from_rlp import IntsSequence, RLPItem, extractData
from starknet.lib.words64 import extract_nibble

func count_shared_prefix_len{ range_check_ptr, bitwise_ptr : BitwiseBuiltin* }(
    path_offset: felt,
    path: IntsSequence,
    proof: IntsSequence,
    leading_leaf_node_rlp_item: RLPItem) -> (new_path_offset: felt):
    alloc_locals

    let (local node_path_decoded: IntsSequence) = extractData(proof.element, proof.element_size_words, leading_leaf_node_rlp_item.length)

    # TODO assert input_decoded len > 0

    # Extract node_path
    let (first_nibble) = extract_nibble(input_decoded.element[0], 0)

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
end

func count_shared_prefix_len_rec{ range_check_ptr, bitwise_ptr : BitwiseBuiltin* }(
    path_offset: felt,
    path: IntsSequence,
    proof: IntsSequence,
    skip_nibbles: felt,
    current_node_path_word_index: felt,
    current_path_word_index: felt,
    current_node_path_nibble_index: felt,
    current_path_nibble_index: felt,
    current_index: felt) -> (res: felt):
end