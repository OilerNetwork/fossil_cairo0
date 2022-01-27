%lang starknet
%builtins pedersen range_check ecdsa bitwise

from starkware.cairo.common.cairo_builtins import BitwiseBuiltin
from starknet.lib.blockheader_rlp_extractor import (
    decode_parent_hash,
    decode_uncles_hash,
    decode_beneficiary,
    decode_state_root,
    decode_transactions_root,
    decode_receipts_root,
    decode_difficulty,
    decode_block_number,
    decode_gas_limit,
    decode_gas_used,
    decode_timestamp,
    decode_base_fee,
    Keccak256Hash,
    Address
)
from starknet.types import IntsSequence

@view
func test_decode_parent_hash{ range_check_ptr }(block_rlp_len_bytes: felt, block_rlp_len: felt, block_rlp: felt*) -> (res: Keccak256Hash):
    alloc_locals
    local input: IntsSequence = IntsSequence(block_rlp, block_rlp_len, block_rlp_len_bytes)
    let (local parent_hash: Keccak256Hash) = decode_parent_hash(input)
    return (parent_hash)
end

@view
func test_decode_uncles_hash{ range_check_ptr }(block_rlp_len_bytes: felt, block_rlp_len: felt, block_rlp: felt*) -> (res: Keccak256Hash):
    alloc_locals
    local input: IntsSequence = IntsSequence(block_rlp, block_rlp_len, block_rlp_len_bytes)
    let (local uncles_hash: Keccak256Hash) = decode_uncles_hash(input)
    return (uncles_hash)
end

@view
func test_decode_beneficiary{ range_check_ptr }(block_rlp_len_bytes: felt, block_rlp_len: felt, block_rlp: felt*) -> (res: Address):
    alloc_locals
    local input: IntsSequence = IntsSequence(block_rlp, block_rlp_len, block_rlp_len_bytes)
    let (local beneficiary: Address) = decode_beneficiary(input)
    return (beneficiary)
end

@view
func test_decode_state_root{ range_check_ptr }(block_rlp_len_bytes: felt, block_rlp_len: felt, block_rlp: felt*) -> (res: Keccak256Hash):
    alloc_locals
    local input: IntsSequence = IntsSequence(block_rlp, block_rlp_len, block_rlp_len_bytes)
    let (local state_root: Keccak256Hash) = decode_state_root(input)
    return (state_root)
end

@view
func test_decode_transactions_root{ range_check_ptr }(block_rlp_len_bytes: felt, block_rlp_len: felt, block_rlp: felt*) -> (res: Keccak256Hash):
    alloc_locals
    local input: IntsSequence = IntsSequence(block_rlp, block_rlp_len, block_rlp_len_bytes)
    let (local transactions_root: Keccak256Hash) = decode_transactions_root(input)
    return (transactions_root)
end

@view
func test_decode_receipts_root{ range_check_ptr }(block_rlp_len_bytes: felt, block_rlp_len: felt, block_rlp: felt*) -> (res: Keccak256Hash):
    alloc_locals
    local input: IntsSequence = IntsSequence(block_rlp, block_rlp_len, block_rlp_len_bytes)
    let (local receipts_root: Keccak256Hash) = decode_receipts_root(input)
    return (receipts_root)
end

@view
func test_decode_difficulty{ range_check_ptr }(block_rlp_len_bytes: felt, block_rlp_len: felt, block_rlp: felt*) -> (res: felt):
    alloc_locals
    local input: IntsSequence = IntsSequence(block_rlp, block_rlp_len, block_rlp_len_bytes)
    return decode_difficulty(input)
end

@view
func test_decode_block_number{ range_check_ptr }(block_rlp_len_bytes: felt, block_rlp_len: felt, block_rlp: felt*) -> (res: felt):
    alloc_locals
    local input: IntsSequence = IntsSequence(block_rlp, block_rlp_len, block_rlp_len_bytes)
    return decode_block_number(input)
end

@view
func test_decode_gas_limit{ range_check_ptr }(block_rlp_len_bytes: felt, block_rlp_len: felt, block_rlp: felt*) -> (res: felt):
    alloc_locals
    local input: IntsSequence = IntsSequence(block_rlp, block_rlp_len, block_rlp_len_bytes)
    return decode_gas_limit(input)
end

@view
func test_decode_gas_used{ range_check_ptr }(block_rlp_len_bytes: felt, block_rlp_len: felt, block_rlp: felt*) -> (res: felt):
    alloc_locals
    local input: IntsSequence = IntsSequence(block_rlp, block_rlp_len, block_rlp_len_bytes)
    return decode_gas_used(input)
end

@view
func test_decode_timestamp{ range_check_ptr }(block_rlp_len_bytes: felt, block_rlp_len: felt, block_rlp: felt*) -> (res: felt):
    alloc_locals
    local input: IntsSequence = IntsSequence(block_rlp, block_rlp_len, block_rlp_len_bytes)
    return decode_timestamp(input)
end

@view
func test_decode_base_fee{ range_check_ptr }(block_rlp_len_bytes: felt, block_rlp_len: felt, block_rlp: felt*) -> (res: felt):
    alloc_locals
    local input: IntsSequence = IntsSequence(block_rlp, block_rlp_len, block_rlp_len_bytes)
    return decode_base_fee(input)
end