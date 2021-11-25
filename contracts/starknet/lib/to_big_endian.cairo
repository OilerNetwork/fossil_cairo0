from starkware.cairo.common.cairo_builtins import BitwiseBuiltin
from starkware.cairo.common.math import assert_le

func to_big_endian{ range_check_ptr, bitwise_ptr : BitwiseBuiltin* }(word: felt) -> (res: felt):
    # verifies word fits in 64bits
    assert_le(word, 9223372036854775807)
    return (word)
end