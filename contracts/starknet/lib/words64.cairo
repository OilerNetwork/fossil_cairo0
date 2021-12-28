from starkware.cairo.common.cairo_builtins import BitwiseBuiltin
from starkware.cairo.common.math import assert_le, unsigned_div_rem
from starknet.lib.bitshift import bitshift_right


func extract_nibble{ range_check_ptr, bitwise_ptr : BitwiseBuiltin* }(word: felt, position: felt) -> (res: felt):
    assert_le(position, 15) # Ensures that the extracted nibble is not out of word range
    let (shifted) = bitshift_right(word, 15 * 4 - position * 4)
    let (q, r) = unsigned_div_rem(shifted, 0x10)
    return (r)
end