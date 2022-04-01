from starkware.cairo.common.math import assert_le
from starkware.cairo.common.math import unsigned_div_rem
from starknet.lib.pow import pow


func bitshift_right{ range_check_ptr }(word: felt, num_bits: felt) -> (shifted: felt):
    # verifies word fits in 64bits
    assert_le(word, 2**64 - 1)

    # verifies shifted bits are not above 64
    assert_le(num_bits, 64)
    
    let (divider) = pow(2, num_bits)
    let (left_part, _) = unsigned_div_rem(word, divider)
    return (left_part)
end

func bitshift_left{ range_check_ptr }(word: felt, num_bits: felt) -> (shifted: felt):
    # verifies word fits in 64bits
    assert_le(word, 2**64 - 1)

    # verifies shifted bits are not above 64
    assert_le(num_bits, 64)

    let (multiplicator) = pow(2, num_bits)
    let k = word * multiplicator
    let (q, r) = unsigned_div_rem(k, 2**64)
    return (r)
end
