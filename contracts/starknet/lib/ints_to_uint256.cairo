%lang starknet

from starkware.cairo.common.cairo_builtins import BitwiseBuiltin
from starkware.cairo.common.uint256 import Uint256, uint256_add
from starkware.cairo.common.math import unsigned_div_rem, assert_nn_le
from starkware.cairo.common.math_cmp import is_le
from starkware.cairo.common.pow import pow
from starkware.cairo.common.bitwise import bitwise_and

from starknet.types import IntsSequence

const MASK_LOW = 2 ** 64

func ints_to_uint256{range_check_ptr, bitwise_ptr : BitwiseBuiltin*}(ints : IntsSequence) -> (
        res : Uint256):
    let elements = ints.element
    let elements_len = ints.element_size_words
    let elements_bytes_len = ints.element_size_bytes
    if elements_len == 1:
        return (Uint256(elements[0], 0))
    end
    assert_nn_le(elements_len, 5)  # The max int sequence length for a uint256 is 4
    let (_, rem) = unsigned_div_rem(elements_bytes_len, 8)
    let initial : Uint256 = Uint256(elements[elements_len - 1], 0)
    if rem == 0:
        let (res) = ints_to_uint256_rec(elements_len - 1, elements, initial, 64)
    else:
        let (res) = ints_to_uint256_rec(elements_len - 1, elements, initial, rem * 8)
    end
    return (res)
end

func ints_to_uint256_rec{range_check_ptr, bitwise_ptr : BitwiseBuiltin*}(
        elements_len : felt, elements : felt*, sum : Uint256, shift : felt) -> (out : Uint256):
    alloc_locals
    if elements_len == 0:
        return (sum)
    end
    # 3 cases:
    # shift < 64 just add num to low
    # 64 < shift < 128 mask bits above and below 128 and add each bit to high and low
    # shift > 128 just add num to high

    let (case3) = is_le(128, shift)
    if case3 == 1:
        let (factor3) = pow(2, shift - 128)
        let num = elements[elements_len - 1] * factor3
        let next : Uint256 = Uint256(low=0, high=num)
        let (new_sum, _) = uint256_add(sum, next)
        let (out) = ints_to_uint256_rec(elements_len - 1, elements, new_sum, shift + 64)
    else:
        let (local factor) = pow(2, shift)
        let (case1) = is_le(shift, 64)
        if case1 == 1:
            let num = elements[elements_len - 1] * factor
            let next : Uint256 = Uint256(num, 0)
            let (new_sum, _) = uint256_add(sum, next)
            let (out) = ints_to_uint256_rec(elements_len - 1, elements, new_sum, shift + 64)
        else:
            # case2
            let (factor2) = pow(2, 128 - shift)
            let mask_h = factor2 - 1
            let (temp_l) = bitwise_and(elements[elements_len - 1], mask_h)
            let num_l = temp_l * factor
            let mask_l = MASK_LOW - factor2
            let (temp_h) = bitwise_and(elements[elements_len - 1], mask_l)
            let (num_h, _) = unsigned_div_rem(temp_h, factor2)
            let next : Uint256 = Uint256(num_l, num_h)
            let (new_sum, _) = uint256_add(sum, next)
            let (out) = ints_to_uint256_rec(elements_len - 1, elements, new_sum, shift + 64)
        end
    end
    return (out)
end
