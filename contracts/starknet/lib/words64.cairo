from starkware.cairo.common.cairo_builtins import BitwiseBuiltin
from starkware.cairo.common.math import assert_le, unsigned_div_rem
from starknet.lib.bitshift import bitshift_right
from starknet.lib.extract_from_rlp import IntsSequence


# TODO include len
func extract_nibble{ range_check_ptr, bitwise_ptr : BitwiseBuiltin* }(word: felt, word_len_bytes: felt, position: felt) -> (res: felt):
    assert_le(position, 15) # Ensures that the extracted nibble is not out of word range
    let (shifted) = bitshift_right(word, 15 * 4 - position * 4)
    let (q, r) = unsigned_div_rem(shifted, 0x10)
    return (r)
end

# TODO write an extract nibble that extracts not from single word but from ints sequence
func extract_nibble_from_words{ range_check_ptr, bitwise_ptr : BitwiseBuiltin* }(input: IntsSequence, position: felt) -> (res: felt):
    alloc_locals
    let (word_index, nibble_index) = unsigned_div_rem(position, 16)

    # Is 0 when it is last word
    let (is_last_word) = input.element_size_words - word_index - 1

    if is_last_word == 0:
        let (_, last_word_len) = unsigned_div_rem(input.element_size_bytes, 8)
        local proper_len
        
        if last_word_len == 0:
            proper_len = 8
        else:
            proper_len = last_word_len
        end

        return extract_nibble(input.elements[word_index], proper_len, nibble_index)
    else:
        return extract_nibble(input.elements[word_index], 8, nibble_index)
    end
end