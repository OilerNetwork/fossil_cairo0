%lang starknet
%builtins pedersen range_check ecdsa

from starknet.lib.header_rlp_decoders import extract_from_rlp

@view
func test_extract_from_rlp{range_check_ptr}(start_pos: felt, size: felt, rlp_len: felt, rlp: felt*) -> (res_len:felt, res: felt*):
    alloc_locals
    let (local extracted: felt*) = extract_from_rlp{range_check_ptr=range_check_ptr}(
        start_pos=start_pos,
        size=size,
        block_rlp=rlp,
        block_rlp_len=rlp_len)
    return (size, extracted)
end