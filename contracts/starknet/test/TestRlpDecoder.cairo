%lang starknet
%builtins pedersen range_check ecdsa

@view
func extract_from_rlp(block_header_rlp_len: felt, block_header_rlp: felt*) -> (block_number: felt, parent_hash: felt, state_root: felt, receipts_root: felt):
    # Block number position 436
    return (block_header_rlp[2], block_header_rlp[0], block_header_rlp[3], block_header_rlp[5])
end