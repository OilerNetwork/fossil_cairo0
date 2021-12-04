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
    Keccak256Hash,
    Address
)

# @view
# func extractData(block_header_rlp_len: felt, block_header_rlp: felt*) -> (block_number: felt, parent_hash: felt, state_root: felt, receipts_root: felt):
#     # Block number position 436
#     return (block_header_rlp[2], block_header_rlp[0], block_header_rlp[3], block_header_rlp[5])
# end

@view
func test_decode_parent_hash{ range_check_ptr }(block_rlp_len: felt, block_rlp: felt*) -> (res: Keccak256Hash):
    alloc_locals
    let (local parent_hash: Keccak256Hash) = decode_parent_hash(block_rlp=block_rlp, block_rlp_len=block_rlp_len)
    return (parent_hash)
end

@view
func test_decode_uncles_hash{ range_check_ptr }(block_rlp_len: felt, block_rlp: felt*) -> (res: Keccak256Hash):
    alloc_locals
    let (local uncles_hash: Keccak256Hash) = decode_uncles_hash(block_rlp=block_rlp, block_rlp_len=block_rlp_len)
    return (uncles_hash)
end

@view
func test_decode_beneficiary{ range_check_ptr }(block_rlp_len: felt, block_rlp: felt*) -> (res: Address):
    alloc_locals
    let (local beneficiary: Address) = decode_beneficiary(block_rlp=block_rlp, block_rlp_len=block_rlp_len)
    return (beneficiary)
end

@view
func test_decode_state_root{ range_check_ptr }(block_rlp_len: felt, block_rlp: felt*) -> (res: Keccak256Hash):
    alloc_locals
    let (local state_root: Keccak256Hash) = decode_state_root(block_rlp=block_rlp, block_rlp_len=block_rlp_len)
    return (state_root)
end

@view
func test_decode_transactions_root{ range_check_ptr }(block_rlp_len: felt, block_rlp: felt*) -> (res: Keccak256Hash):
    alloc_locals
    let (local transactions_root: Keccak256Hash) = decode_transactions_root(block_rlp=block_rlp, block_rlp_len=block_rlp_len)
    return (transactions_root)
end

@view
func test_decode_receipts_root{ range_check_ptr }(block_rlp_len: felt, block_rlp: felt*) -> (res: Keccak256Hash):
    alloc_locals
    let (local receipts_root: Keccak256Hash) = decode_receipts_root(block_rlp=block_rlp, block_rlp_len=block_rlp_len)
    return (receipts_root)
end

@view
func test_decode_difficulty{ range_check_ptr }(block_rlp_len: felt, block_rlp: felt*) -> (res: felt):
    return decode_difficulty(block_rlp=block_rlp, block_rlp_len=block_rlp_len)
end

@view
func test_decode_block_number{ range_check_ptr }(block_rlp_len: felt, block_rlp: felt*) -> (res: felt):
    return decode_block_number(block_rlp=block_rlp, block_rlp_len=block_rlp_len)
end