from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.cairo_builtins import BitwiseBuiltin

from starkware.cairo.common.alloc import alloc
from starkware.cairo.common.math import unsigned_div_rem

from starkware.cairo.common.cairo_keccak.keccak import keccak_as_words, finalize_keccak

from starknet.lib.swap_endianness import swap_endianness_64
from starknet.types import IntsSequence

func keccak256_auto_finalize{range_check_ptr, keccak_ptr : felt*, bitwise_ptr : BitwiseBuiltin*}(input: IntsSequence) -> (output : felt*):
    alloc_locals
    let keccak_ptr_start = keccak_ptr
    let (local output) = keccak256{keccak_ptr=keccak_ptr}(input)
    finalize_keccak(keccak_ptr_start=keccak_ptr_start, keccak_ptr_end=keccak_ptr)
    return (output)
end

func keccak256{range_check_ptr, keccak_ptr : felt*, bitwise_ptr : BitwiseBuiltin*}(input: IntsSequence) -> (output : felt*):
    alloc_locals
    let (local input_le: IntsSequence) = to_le(input)

    let (keccak_hash) = keccak_as_words{keccak_ptr=keccak_ptr}(input_le.element, input_le.element_size_bytes)

    local word_1_le = keccak_hash[0]
    local word_2_le = keccak_hash[1]
    local word_3_le = keccak_hash[2]
    local word_4_le = keccak_hash[3]

    let (local word_1_be) = swap_endianness_64(word_1_le, 8)
    let (local word_2_be) = swap_endianness_64(word_2_le, 8)
    let (local word_3_be) = swap_endianness_64(word_3_le, 8)
    let (local word_4_be) = swap_endianness_64(word_4_le, 8)

    let (local output) = alloc()

    assert output[0] = word_1_be
    assert output[1] = word_2_be
    assert output[2] = word_3_be
    assert output[3] = word_4_be
    return (output)
end 

func to_le{range_check_ptr, bitwise_ptr : BitwiseBuiltin*}(input: IntsSequence) -> (res: IntsSequence):
    alloc_locals
    let (local element_new) = alloc()
    to_le_rec(input, 0, element_new)

    local size_words = input.element_size_words
    local size_bytes = input.element_size_bytes

    local res: IntsSequence = IntsSequence(element_new, size_words, size_bytes)
    return (res)
end

func to_le_rec{range_check_ptr, bitwise_ptr : BitwiseBuiltin*}(input: IntsSequence, acc_len: felt, acc: felt*):
    alloc_locals
    if acc_len == input.element_size_words:
        return ()
    end

    local word_size_bytes

    local range_check_ptr : felt = range_check_ptr

    if acc_len == input.element_size_words - 1:
        let (q, r) = unsigned_div_rem(input.element_size_bytes, 8)
        # is full word
        if r == 0:
            word_size_bytes = 8
        else:
            word_size_bytes = r
        end
        tempvar range_check_ptr = range_check_ptr
    else:
        word_size_bytes = 8
        tempvar range_check_ptr = range_check_ptr
    end

    local current_word = input.element[acc_len]

    let (local le_word) = swap_endianness_64(current_word, word_size_bytes)

    assert acc[acc_len] = le_word
    return to_le_rec(input, acc_len + 1, acc)
end