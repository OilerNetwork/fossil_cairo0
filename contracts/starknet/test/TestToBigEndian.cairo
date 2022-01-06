%lang starknet
%builtins pedersen range_check ecdsa bitwise

from starkware.cairo.common.cairo_builtins import BitwiseBuiltin
from starknet.lib.swap_endianness import swap_endianness_64, swap_endianness_four_words
from starknet.types import IntsSequence

@view
func test_to_big_endian{ range_check_ptr, bitwise_ptr : BitwiseBuiltin* }(word: felt, size: felt) -> (res: felt):
    let (res) = swap_endianness_64(word, size)
    return (res)
end

# @view
# func test_many_words_to_big_endian{ range_check_ptr, bitwise_ptr : BitwiseBuiltin* }(input_len: felt, input: felt*, input_size_bytes: felt) -> (res_len_bytes: felt, res_len:felt, res: felt*):
#     let input_seq: IntsSequence = IntsSequence(input, input_len, input_size_bytes)

#     let (res) = swap_endianness_many_words(input_seq)

#     return (res.element_size_bytes, res.element_size_words, res.element)
# end

@view
func test_four_words_to_big_endian{ range_check_ptr, bitwise_ptr : BitwiseBuiltin* }(input_len: felt, input: felt*, input_size_bytes: felt) -> (res_len_bytes: felt, res_len:felt, res: felt*):
    let input_seq: IntsSequence = IntsSequence(input, input_len, input_size_bytes)

    let (res) = swap_endianness_four_words(input_seq)

    return (res.element_size_bytes, res.element_size_words, res.element)
end