from starkware.cairo.common.cairo_builtins import BitwiseBuiltin
from starkware.cairo.common.math import unsigned_div_rem
from starkware.cairo.common.math_cmp import is_le
from starkware.cairo.common.alloc import alloc

from starknet.lib.bitshift import bitshift_right, bitshift_left
from starknet.lib.pow import pow

struct Keccak256Hash:
    member word_1 : felt
    member word_2 : felt
    member word_3 : felt
    member word_4 : felt
end

const parent_hash_start_bit = 16
const parent_hash_end_bit = 16 + 256

func extract_from_rlp{ range_check_ptr }(start_pos: felt, size: felt, block_rlp: felt*, block_rlp_len: felt) -> (res_size: felt, res: felt*):
    alloc_locals

    let (start_word, left_shift) = unsigned_div_rem(start_pos, 8)
    let (end_word_tmp, end_pos_tmp) = unsigned_div_rem(start_pos + size, 8)

    local end_pos
    local end_word

    if end_pos_tmp == 0:
        end_pos = 8
        end_word = end_word_tmp - 1
    else:
        end_pos = end_pos_tmp
        end_word = end_word_tmp
    end


    local right_shift = 8 - left_shift

    let (full_words, remainder) = unsigned_div_rem(size, 8)

    let (local words_shifted : felt*) = alloc()

    if full_words != 0:
        shift_words{ range_check_ptr = range_check_ptr }(
            current_index=full_words - 1,
            start_word=start_word,
            left_shift=left_shift,
            right_shift=right_shift,
            block_rlp=block_rlp,
            block_rlp_len=block_rlp_len,
            accumulator=words_shifted,
            accumulator_len=full_words
        )
        tempvar range_check_ptr = range_check_ptr
    else:
        tempvar range_check_ptr = range_check_ptr
    end

    local range_check_ptr = range_check_ptr

    if remainder != 0:
        let (above_8) = is_le(9, remainder + left_shift)
        if above_8 == 1:
            let (left_part) = bitshift_left(block_rlp[end_word - 1], left_shift * 8)
            let (right_part) = bitshift_right(block_rlp[end_word], right_shift * 8)
            let final_word = left_part + right_part

            let (final_word_shifted) = bitshift_right(final_word, (8 - remainder) * 8)

            let (local divider: felt) = pow(2, remainder*8)
            let (_, new_word) = unsigned_div_rem(final_word_shifted, divider)

            assert words_shifted[full_words] = new_word

            tempvar range_check_ptr = range_check_ptr
        else:
            let (final_word_shifted) = bitshift_right(block_rlp[end_word], (8 - end_pos) * 8)

            let (local divider: felt) = pow(2, (end_pos-left_shift)*8)
            let (_, new_word) = unsigned_div_rem(final_word_shifted, divider)

            assert words_shifted[full_words] = new_word

            tempvar range_check_ptr = range_check_ptr
        end
        tempvar range_check_ptr = range_check_ptr
        return (res_size=full_words+1, res=words_shifted)
    else:
        tempvar range_check_ptr = range_check_ptr
        return (res_size=full_words, res=words_shifted)
    end
end

func shift_words{ range_check_ptr }(
    current_index: felt,
    start_word: felt,
    left_shift: felt,
    right_shift: felt,
    block_rlp: felt*,
    block_rlp_len: felt,
    accumulator: felt*,
    accumulator_len: felt):
    alloc_locals

    if current_index == -1:
        tempvar range_check_ptr = range_check_ptr
        ret
    else:
        if left_shift != 0:
            let (left_part) = bitshift_left(block_rlp[start_word + current_index], left_shift * 8)
            let (right_part) = bitshift_right(block_rlp[start_word + current_index + 1], right_shift * 8)
        
            local new_word = left_part + right_part
            let (local divider: felt) = pow(2, 64)
            let (_, new_word_masked) = unsigned_div_rem(new_word, divider)

            assert accumulator[current_index] = new_word_masked
            tempvar range_check_ptr = range_check_ptr
        else:
            assert accumulator[current_index] = block_rlp[start_word + current_index]
            tempvar range_check_ptr = range_check_ptr
        end

        shift_words{ range_check_ptr = range_check_ptr }(
            current_index=current_index - 1,
            start_word=start_word,
            left_shift=left_shift,
            right_shift=right_shift,
            block_rlp=block_rlp,
            block_rlp_len=block_rlp_len,
            accumulator=accumulator,
            accumulator_len=accumulator_len)

        tempvar range_check_ptr = range_check_ptr
    end
    ret
end


### Elements decoder 

func decode_parent_hash{ range_check_ptr }(block_rlp: felt*, block_rlp_len: felt) -> (res: Keccak256Hash):
    alloc_locals
    let (parent_hash) = extract_from_rlp(32, 32 * 8, block_rlp, block_rlp_len)
    local hash: Keccak256Hash = Keccak256Hash(
        word_1=parent_hash[0],
        word_2=parent_hash[1],
        word_3=parent_hash[2],
        word_4=parent_hash[3]
    )
    return (hash)
end
