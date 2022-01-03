%lang starknet
%builtins pedersen range_check ecdsa

from starknet.lib.comp_arr import arr_eq

@view
func test_comp_arr(
    a_len: felt,
    a: felt*,
    b_len: felt,
    b: felt*) -> (res: felt):

    return arr_eq(a=a, a_len=a_len, b=b, b_len=b_len)
end