from starkware.cairo.common.math import assert_le, unsigned_div_rem
from starkware.cairo.common.math_cmp import is_le

from starknet.types import Address
from starknet.lib.pow import pow
from starknet.lib.bitshift import bitshift_right, bitshift_left

func address_words64_to_160bit{ range_check_ptr }(input: Address) -> (res: felt):
    alloc_locals
    let (local word_1_exponent) = pow(2, 8 * 12)
    let (local word_2_exponent) = pow(2, 8 * 4)
    
    let result = (input.word_1 * word_1_exponent) + (input.word_2 * word_2_exponent) + input.word_3
    return (result)
end

func address_160bit_to_words64{ range_check_ptr }(input: felt) -> (res: Address):
    alloc_locals

    let (local eigth_byte_exponent) = pow(2, 8 * 8)
    let (local four_byte_exponent) = pow(2, 4 * 8)
    
    let (tmp, third_word) = unsigned_div_rem(input, four_byte_exponent)

    let third_word_max_size = 2**32 - 1
    assert_le(third_word, third_word_max_size)

    let (first_word, second_word) = unsigned_div_rem(tmp, eigth_byte_exponent)
    local res: Address = Address(first_word, second_word, third_word)
    return (res)
end