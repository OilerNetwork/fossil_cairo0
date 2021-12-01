%lang starknet
%builtins pedersen range_check ecdsa bitwise

from starkware.cairo.common.cairo_builtins import BitwiseBuiltin
from starknet.lib.swap_endianness import swap_endianness_64

@view
func test_to_big_endian{ range_check_ptr, bitwise_ptr : BitwiseBuiltin* }(word: felt, size: felt) -> (res: felt):
    let (res) = swap_endianness_64(word, size)
    return (res)
end