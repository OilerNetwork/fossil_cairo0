%lang starknet
%builtins pedersen range_check ecdsa

from starknet.lib.header_rlp_decoders import decode_parent_hash, Keccak256Hash

@view
func extract_from_rlp(block_header_rlp_len: felt, block_header_rlp: felt*) -> (block_number: felt, parent_hash: felt, state_root: felt, receipts_root: felt):
    # Block number position 436
    return (block_header_rlp[2], block_header_rlp[0], block_header_rlp[3], block_header_rlp[5])
end

@view
func test_decode_parent_hash(block_rlp_len: felt, block_rlp: felt*) -> (res: Keccak256Hash):
    alloc_locals
    let (local parent_hash: Keccak256Hash) = decode_parent_hash(block_rlp=block_rlp, block_rlp_len=block_rlp_len)
    return (parent_hash)
end