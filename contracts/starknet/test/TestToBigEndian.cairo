%lang starknet
%builtins pedersen range_check ecdsa bitwise

from starkware.cairo.common.cairo_builtins import BitwiseBuiltin
from starknet.lib.to_big_endian import to_big_endian

@view
func test_to_big_endian{ range_check_ptr, bitwise_ptr : BitwiseBuiltin* }(word: felt) -> (res: felt):
    let (res) = to_big_endian(word)
    return (res)
end