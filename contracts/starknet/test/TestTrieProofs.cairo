%lang starknet
%builtins pedersen range_check ecdsa bitwise

from starkware.cairo.common.alloc import alloc

from starknet.lib.extract_from_rlp import IntsSequence, RLPItem
from starknet.lib.trie_proofs import count_shared_prefix_len, get_next_hash
from starknet.types import Keccak256Hash


@view
func test_count_shared_prefix_len{ range_check_ptr }(
    path_offset: felt,
    path_values_len: felt,
    path_values: felt*,
    path_size_bytes: felt,
    element_rlp_values_len: felt,
    element_rlp_values: felt*,
    element_rlp_size_bytes: felt,
    node_path_item_data_pos: felt,
    node_path_item_length: felt) -> (res: felt):
    alloc_locals

    let path: IntsSequence = IntsSequence(path_values, path_values_len, path_size_bytes)
    let element_rlp: IntsSequence = IntsSequence(element_rlp_values, element_rlp_values_len, element_rlp_size_bytes)

    let node_path_item: RLPItem = RLPItem(node_path_item_data_pos, node_path_item_length)

    return count_shared_prefix_len(
        path_offset,
        path,
        element_rlp,
        node_path_item)
end


@view
func test_get_next_hash{ range_check_ptr }(
    rlp_input_values_len: felt,
    rlp_input_values: felt*,
    rlp_input_values_size_bytes: felt,
    rlp_node_data_pos: felt,
    rlp_node_data_length: felt) -> (res: Keccak256Hash):
    alloc_locals

    let rlp_input: IntsSequence = IntsSequence(rlp_input_values, rlp_input_values_len, rlp_input_values_size_bytes)
    let rlp_node: RLPItem = RLPItem(rlp_node_data_pos, rlp_node_data_length)

    return get_next_hash(
        rlp_input,
        rlp_node)
end