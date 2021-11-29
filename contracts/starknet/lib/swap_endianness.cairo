from starkware.cairo.common.cairo_builtins import BitwiseBuiltin
from starkware.cairo.common.math import assert_le
from starkware.cairo.common.alloc import alloc
from starkware.cairo.common.math import assert_nn_le, unsigned_div_rem
from starkware.cairo.common.math_cmp import is_in_range

func swap_endianness_64{ range_check_ptr, bitwise_ptr : BitwiseBuiltin* }(input: felt) -> (output: felt):
    alloc_locals
    let (local output : felt*) = alloc()

    # verifies word fits in 64bits
    assert_le(input, 2**64 - 1)

    # swapped_bytes = ((word & 0xFF00FF00FF00FF00) >> 8) | ((word & 0x00FF00FF00FF00FF) << 8)
    let (left_part, _) = unsigned_div_rem(input, 256)

    assert bitwise_ptr[0].x = left_part
    assert bitwise_ptr[0].y = 0x00FF00FF00FF00FF
    
    assert bitwise_ptr[1].x = input * 256
    assert bitwise_ptr[1].y = 0xFF00FF00FF00FF00
    
    let swapped_bytes = bitwise_ptr[0].x_and_y + bitwise_ptr[1].x_and_y

    # swapped_2byte_pair = ((swapped_bytes & 0xFFFF0000FFFF0000) >> 16) | ((swapped_bytes & 0x0000FFFF0000FFFF) << 16)
    let (left_part2, _) = unsigned_div_rem(swapped_bytes, 2**16)

    assert bitwise_ptr[2].x = left_part2
    assert bitwise_ptr[2].y = 0x0000FFFF0000FFFF
    
    assert bitwise_ptr[3].x = swapped_bytes * 2**16
    assert bitwise_ptr[3].y = 0xFFFF0000FFFF0000
    
    let swapped_2bytes = bitwise_ptr[2].x_and_y + bitwise_ptr[3].x_and_y

    # swapped_4byte_pair = (swapped_2byte_pair >> 32) | ((swapped_2byte_pair << 32) % 2**64)
    let (left_part4, _) = unsigned_div_rem(swapped_2bytes, 2**32)

    assert bitwise_ptr[4].x = swapped_2bytes * 2**32
    assert bitwise_ptr[4].y = 0xFFFFFFFF00000000
    
    let swapped_4bytes = left_part4 + bitwise_ptr[4].x_and_y

    let bitwise_ptr = bitwise_ptr + 5 * BitwiseBuiltin.SIZE

    # Some Shiva-inspired code here
    local shift

    let (local is_above_56bits: felt) = is_in_range(input, 2**56, 2**64)
    if is_above_56bits == 1:
        assert shift = 1
    else:
        let (local is_above_48bits: felt) = is_in_range(input, 2**48, 2**56)
        if is_above_48bits == 1:
            assert shift = 2**8
        else:
            let (local is_above_40bits: felt) = is_in_range(input, 2**40, 2**48)
            if is_above_40bits == 1:
                assert shift = 2**16
            else:
                let (local is_above_32bits: felt) = is_in_range(input, 2**32, 2**40)
                if is_above_32bits == 1:
                    assert shift = 2**24
                else:
                    let (local is_above_24bits: felt) = is_in_range(input, 2**24, 2**32)
                    if is_above_24bits == 1:
                        assert shift = 2**32
                    else:
                        let (local is_above_16bits: felt) = is_in_range(input, 2**16, 2**24)
                        if is_above_16bits == 1:
                            assert shift = 2**40
                        else:
                            let (local is_above_8bits: felt) = is_in_range(input, 2**8, 2**16)
                            if is_above_8bits == 1:
                                assert shift = 2**48
                            else:
                                let (local is_above_1: felt) = is_in_range(input, 1, 2**8)
                                if is_above_1 == 1:
                                    assert shift = 2**56
                                else:
                                    if input == 0:
                                        assert shift = 0
                                    end
                                end
                            end
                        end
                    end
                end
            end
        end
    end

    if shift == 1:
        return (swapped_4bytes)
    else:
        if shift == 0:
            return (swapped_4bytes)
        else:
            let (shifted_4bytes, _) = unsigned_div_rem(swapped_4bytes, shift)
            return (shifted_4bytes)
        end
    end
end