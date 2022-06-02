%lang starknet
%builtins pedersen range_check ecdsa bitwise

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.cairo_builtins import BitwiseBuiltin
from starkware.starknet.common.syscalls import get_caller_address
from starkware.cairo.common.alloc import alloc
from starkware.cairo.common.math import unsigned_div_rem

from starkware.cairo.common.cairo_keccak.keccak import keccak_as_words, finalize_keccak

from starknet.lib.swap_endianness import swap_endianness_64
from starknet.types import IntsSequence

struct Keccak256Hash:
    member word_1 : felt
    member word_2 : felt
    member word_3 : felt
    member word_4 : felt
end


# Input little endian
# Output little endian
@view
func test_keccak256_std{range_check_ptr, bitwise_ptr : BitwiseBuiltin*}(keccak_input_length: felt, input_len : felt, input : felt*) -> (res: Keccak256Hash):
    alloc_locals
    let (local keccak_ptr : felt*) = alloc()
    let keccak_ptr_start = keccak_ptr

    local input_ints_sequence: IntsSequence = IntsSequence(input, input_len, keccak_input_length)

    let (keccak_hash) = keccak_as_words{keccak_ptr=keccak_ptr}(input_ints_sequence.element, input_ints_sequence.element_size_bytes)
    finalize_keccak(keccak_ptr_start=keccak_ptr_start, keccak_ptr_end=keccak_ptr)

    local hash: Keccak256Hash = Keccak256Hash(
        word_1=keccak_hash[0],
        word_2=keccak_hash[1],
        word_3=keccak_hash[2],
        word_4=keccak_hash[3]
    )

    return (hash)
end

# Input big endian
# Output big endian
@view
func test_keccak256_std_be{range_check_ptr, bitwise_ptr : BitwiseBuiltin*}(keccak_input_length: felt, input_len : felt, input : felt*) -> (res: Keccak256Hash):
    alloc_locals
    let (local keccak_ptr : felt*) = alloc()
    let keccak_ptr_start = keccak_ptr

    local input_ints_sequence_be: IntsSequence = IntsSequence(input, input_len, keccak_input_length)
    let (local input_ints_sequence: IntsSequence) = to_le(input_ints_sequence_be)

    let (keccak_hash) = keccak_as_words{keccak_ptr=keccak_ptr}(input_ints_sequence.element, input_ints_sequence.element_size_bytes)
    finalize_keccak(keccak_ptr_start=keccak_ptr_start, keccak_ptr_end=keccak_ptr)

    local word_1_le = keccak_hash[0]
    local word_2_le = keccak_hash[1]
    local word_3_le = keccak_hash[2]
    local word_4_le = keccak_hash[3]

    let (local word_1_be) = swap_endianness_64(word_1_le, 8)
    let (local word_2_be) = swap_endianness_64(word_2_le, 8)
    let (local word_3_be) = swap_endianness_64(word_3_le, 8)
    let (local word_4_be) = swap_endianness_64(word_4_le, 8)

    local hash: Keccak256Hash = Keccak256Hash(
        word_1=word_1_be,
        word_2=word_2_be,
        word_3=word_3_be,
        word_4=word_4_be
    )

    return (hash)
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