from starkware.cairo.common.cairo_builtins import BitwiseBuiltin
from starkware.cairo.common.math import unsigned_div_rem
from starkware.cairo.common.alloc import alloc

from starknet.lib.bitshift import bitshift_right, bitshift_left

struct Keccak256Hash:
    member word_1 : felt
    member word_2 : felt
    member word_3 : felt
    member word_4 : felt
end

const parent_hash_start_bit = 16
const parent_hash_end_bit = 16 + 256

func extract_from_block_rlp{
        range_check_ptr,
        bitwise_ptr: BitwiseBuiltin*
    }(bit_pos: felt, size_bits: felt, block_rlp: felt*, block_rlp_len: felt) -> (res: felt*):
    alloc_locals

    let (start_word, start_pos) = unsigned_div_rem(bit_pos, 64)

    local left_shift = start_pos
    local right_shift = 64 - left_shift

    let (full_words_affected, remainer) = unsigned_div_rem(size_bits, 64)

    local words_affected

    if remainer == 0:
        words_affected = full_words_affected
    else:
        words_affected = full_words_affected + 1
    end

    let (words_shifted : felt*) = alloc()

    shift_words{ range_check_ptr = range_check_ptr, bitwise_ptr = bitwise_ptr }(
        current_index=words_affected,
        start_word=start_word,
        left_shift=left_shift,
        right_shift=right_shift,
        block_rlp=block_rlp,
        block_rlp_len=block_rlp_len,
        accumulator=words_shifted,
        accumulator_len=words_affected
    )

    return (words_shifted)
end

func shift_words{
        range_check_ptr,
        bitwise_ptr: BitwiseBuiltin*
    }(
    current_index: felt,
    start_word: felt,
    left_shift: felt,
    right_shift: felt,
    block_rlp: felt*,
    block_rlp_len: felt,
    accumulator: felt*,
    accumulator_len: felt):
    alloc_locals

    if current_index == 0:
        tempvar bitwise_ptr = bitwise_ptr
        tempvar range_check_ptr = range_check_ptr

        let (left_part) = bitshift_left(block_rlp[start_word + current_index], left_shift)
        let (right_part) = bitshift_right(block_rlp[start_word + current_index + 1], right_shift)
    
        local new_word = left_part + right_part

        assert accumulator[current_index] = new_word
    else:
        tempvar bitwise_ptr = bitwise_ptr
        tempvar range_check_ptr = range_check_ptr

        shift_words{ range_check_ptr = range_check_ptr, bitwise_ptr = bitwise_ptr }(
            current_index=current_index - 1,
            start_word=start_word,
            left_shift=left_shift,
            right_shift=right_shift,
            block_rlp=block_rlp,
            block_rlp_len=block_rlp_len,
            accumulator=accumulator,
            accumulator_len=accumulator_len)
    end
    ret
end
    

func decode_parent_hash(block_rlp: felt*, block_rlp_len: felt) -> (res: Keccak256Hash):
    alloc_locals
    local hash: Keccak256Hash = Keccak256Hash(
        word_1=block_rlp[1],
        word_2=block_rlp[2],
        word_3=block_rlp[3],
        word_4=block_rlp[4]
    )
    return (hash)
end
