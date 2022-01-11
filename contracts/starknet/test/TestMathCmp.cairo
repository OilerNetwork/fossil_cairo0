%lang starknet
%builtins pedersen range_check ecdsa

from starkware.cairo.common.math_cmp import is_le

@view
func test_is_le{ range_check_ptr }(a: felt, b: felt) -> (res: felt):
    return is_le(a - b, -1)
end