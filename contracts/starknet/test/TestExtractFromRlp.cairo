%lang starknet
%builtins pedersen range_check ecdsa

from starknet.lib.extract_from_rlp import extractData, is_rlp_list
from starkware.cairo.common.alloc import alloc

@view
func test_extractData{range_check_ptr}(start_pos: felt, size: felt, rlp_len: felt, rlp: felt*) -> (res_len:felt, res: felt*):
    alloc_locals
    let (local res_len: felt, local extracted: felt*) = extractData(
        start_pos=start_pos,
        size=size,
        block_rlp=rlp,
        block_rlp_len=rlp_len)
    return (res_len, extracted)
end

@view 
func test_is_rlp_list{range_check_ptr}(pos: felt, rlp_len: felt, rlp: felt*) -> (res: felt):
    return is_rlp_list(pos, rlp, rlp_len)
end