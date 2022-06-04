%lang starknet
%builtins pedersen range_check ecdsa bitwise

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.cairo_builtins import BitwiseBuiltin
from starkware.starknet.common.syscalls import get_caller_address
from starkware.cairo.common.alloc import alloc

from starkware.cairo.common.cairo_keccak.keccak import keccak_as_words, finalize_keccak

from starknet.types import IntsSequence
from starknet.lib.keccak_std_be import keccak256_auto_finalize

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

# Input little endian
# Output little endian
@view
func test_keccak256_std_multiple{range_check_ptr, bitwise_ptr : BitwiseBuiltin*}(
    keccak_input_1_length: felt,
    input_1_len : felt,
    input_1 : felt*,
    keccak_input_2_length: felt,
    input_2_len : felt,
    input_2 : felt*
    ) -> (res_1: Keccak256Hash, res_2: Keccak256Hash):
    alloc_locals
    let (local keccak_ptr : felt*) = alloc()
    let keccak_ptr_start = keccak_ptr

    local input_ints_sequence_1: IntsSequence = IntsSequence(input_1, input_1_len, keccak_input_1_length)
    let (keccak_hash_1) = keccak_as_words{keccak_ptr=keccak_ptr}(input_ints_sequence_1.element, input_ints_sequence_1.element_size_bytes)

    local input_ints_sequence_2: IntsSequence = IntsSequence(input_2, input_2_len, keccak_input_2_length)
    let (keccak_hash_2) = keccak_as_words{keccak_ptr=keccak_ptr}(input_ints_sequence_2.element, input_ints_sequence_2.element_size_bytes)

    finalize_keccak(keccak_ptr_start=keccak_ptr_start, keccak_ptr_end=keccak_ptr)

    local hash_1: Keccak256Hash = Keccak256Hash(
        word_1=keccak_hash_1[0],
        word_2=keccak_hash_1[1],
        word_3=keccak_hash_1[2],
        word_4=keccak_hash_1[3]
    )

    local hash_2: Keccak256Hash = Keccak256Hash(
        word_1=keccak_hash_2[0],
        word_2=keccak_hash_2[1],
        word_3=keccak_hash_2[2],
        word_4=keccak_hash_2[3]
    )

    return (hash_1, hash_2)
end

# Input big endian
# Output big endian
@view
func test_keccak256_std_be{range_check_ptr, bitwise_ptr : BitwiseBuiltin*}(keccak_input_length: felt, input_len : felt, input : felt*) -> (res: Keccak256Hash):
    alloc_locals
    let (local keccak_ptr : felt*) = alloc()

    local input_be: IntsSequence = IntsSequence(input, input_len, keccak_input_length)
    let (local result) = keccak256_auto_finalize{keccak_ptr=keccak_ptr}(input_be)

    local hash: Keccak256Hash = Keccak256Hash(
        word_1=result[0],
        word_2=result[1],
        word_3=result[2],
        word_4=result[3]
    )

    return (hash)
end