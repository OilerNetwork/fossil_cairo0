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
    proof_element_values_len: felt,
    proof_element_values: felt*,
    proof_element_size_bytes: felt,
    leading_leaf_node_rlp_item_data_pos: felt,
    leading_leaf_node_rlp_item_length: felt) -> (new_path_offset: felt):
    alloc_locals

    let path: IntsSequence = IntsSequence(path_values, path_values_len, path_size_bytes)
    let proof_element: IntsSequence = IntsSequence(proof_element_values, proof_element_values_len, proof_element_size_bytes)

    let leading_leaf_node_rlp_item: RLPItem = RLPItem(leading_leaf_node_rlp_item_data_pos, leading_leaf_node_rlp_item_length)

    return count_shared_prefix_len(
        path_offset,
        path,
        proof_element,
        leading_leaf_node_rlp_item)
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