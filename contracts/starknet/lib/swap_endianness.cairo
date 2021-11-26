from starkware.cairo.common.cairo_builtins import BitwiseBuiltin
from starkware.cairo.common.math import assert_le
from starkware.cairo.common.math import assert_nn_le, unsigned_div_rem

func swap_endianness_64{ range_check_ptr, bitwise_ptr : BitwiseBuiltin* }(input: felt) -> (output: felt):
    alloc_locals
    let (local output : felt*) = alloc()

    # verifies word fits in 64bits
    assert_le(input, 9223372036854775807)

    # swapped_bytes = ((word & 0xFF00FF00FF00FF00) >> 8) | ((word & 0x00FF00FF00FF00FF) << 8)
    let (left_part, _) = unsigned_div_rem(input, 256)

    assert bitwise_ptr[0].x = left_part
    assert bitwise_ptr[0].y = 0x00FF00FF00FF00FF
    
    assert bitwise_ptr[1].x = input * 256
    assert bitwise_ptr[1].y = 0xFF00FF00FF00FF00
    
    let (swapped_bytes) = bitwise_ptr[0].x_and_y + bitwise_ptr[1].x_and_y

    # swapped_2byte_pair = ((swapped_bytes & 0xFFFF0000FFFF0000) >> 16) | ((swapped_bytes & 0x0000FFFF0000FFFF) << 16)
    let (left_part2, _) = unsigned_div_rem(input, 2**16)

    assert bitwise_ptr[2].x = left_part2
    assert bitwise_ptr[2].y = 0x0000FFFF0000FFFF
    
    assert bitwise_ptr[3].x = input * 2**16
    assert bitwise_ptr[3].y = 0xFFFF0000FFFF0000
    
    let (swapped_2bytes) = bitwise_ptr[2].x_and_y + bitwise_ptr[3].x_and_y

    # swapped_4byte_pair = (swapped_2byte_pair >> 32) | ((swapped_2byte_pair << 32) % 2**64)
    let (left_part4, _) = unsigned_div_rem(input, 2**32)

    assert bitwise_ptr[4].x = input * 2**32
    assert bitwise_ptr[4].y = 0xFFFFFFFF00000000
    
    let (swapped_4bytes) = left_part4 + bitwise_ptr[4].x_and_y

    let bitwise_ptr = bitwise_ptr + 5 * BitwiseBuiltin.SIZE
    return (swapped_4bytes)
end