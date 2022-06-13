%lang starknet
%builtins pedersen range_check ecdsa bitwise

from starkware.cairo.common.cairo_builtins import BitwiseBuiltin
from starkware.cairo.common.alloc import alloc

from starknet.types import IntsSequence, RLPItem, reconstruct_ints_sequence_list
from starknet.lib.trie_proofs import count_shared_prefix_len, get_next_hash, verify_proof
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
    node_path_item_firstByte: felt,
    node_path_item_data_pos: felt,
    node_path_item_length: felt) -> (res: felt):
    alloc_locals

    let path: IntsSequence = IntsSequence(path_values, path_values_len, path_size_bytes)
    let element_rlp: IntsSequence = IntsSequence(element_rlp_values, element_rlp_values_len, element_rlp_size_bytes)

    let node_path_item: RLPItem = RLPItem(node_path_item_firstByte, node_path_item_data_pos, node_path_item_length)

    let (local res) = count_shared_prefix_len(
        path_offset,
        path,
        element_rlp,
        node_path_item)
    return (res)
end


@view
func test_get_next_hash{ range_check_ptr }(
    rlp_input_values_len: felt,
    rlp_input_values: felt*,
    rlp_input_values_size_bytes: felt,
    rlp_node_first_byte: felt,
    rlp_node_data_pos: felt,
    rlp_node_data_length: felt) -> (res_len: felt, res: felt*):
    alloc_locals

    let rlp_input: IntsSequence = IntsSequence(rlp_input_values, rlp_input_values_len, rlp_input_values_size_bytes)
    let rlp_node: RLPItem = RLPItem(rlp_node_first_byte, rlp_node_data_pos, rlp_node_data_length)

    let (local res: IntsSequence) = get_next_hash(rlp_input, rlp_node)
    return (res.element_size_words, res.element)
end


@view
func test_verify_proof{ range_check_ptr, bitwise_ptr : BitwiseBuiltin* }(
    path_size_bytes: felt,
    path_len: felt,
    path: felt*,
    root_hash_size_bytes: felt,
    root_hash_len: felt,
    root_hash: felt*,
    proof_sizes_bytes_len: felt,
    proof_sizes_bytes: felt*,
    proof_sizes_words_len: felt,
    proof_sizes_words: felt*,
    proofs_concat_len: felt,
    proofs_concat: felt*) -> (res_size_bytes: felt, res_len: felt, res: felt*):
    alloc_locals
    local path_arg: IntsSequence = IntsSequence(path, path_len, path_size_bytes)
    local root_hash_arg: IntsSequence = IntsSequence(root_hash, root_hash_len, root_hash_size_bytes)

    let (local proof_arg: IntsSequence*) = alloc()
    reconstruct_ints_sequence_list(
        proofs_concat,
        proofs_concat_len,
        proof_sizes_words,
        proof_sizes_words_len,
        proof_sizes_bytes,
        proof_sizes_bytes_len,
        proof_arg,
        0,
        0,
        0
    )

    let (local result: IntsSequence) = verify_proof(
        path_arg,
        root_hash_arg,
        proof_arg,
        proof_sizes_bytes_len)

    return (result.element_size_bytes, result.element_size_words, result.element)
end
