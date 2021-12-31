%lang starknet
%builtins pedersen range_check ecdsa

from starknet.lib.concat_arr import concat_arr

@view
func test_concat_arr{range_check_ptr}(
    acc_len: felt,
    acc: felt*,
    arr_len: felt,
    arr: felt*) -> (res_len: felt, res: felt*):

    let (res, res_len) = concat_arr(
        acc=acc,
        acc_len=acc_len,
        arr=arr,
        arr_len=arr_len)

    return (res_len, res)
end