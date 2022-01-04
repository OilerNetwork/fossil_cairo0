%lang starknet
%builtins pedersen range_check ecdsa bitwise

from starknet.lib.extract_from_rlp import IntsSequence
from starkware.cairo.common.cairo_builtins import BitwiseBuiltin
from starknet.lib.words64 import extract_nibble, extract_nibble_from_words

@view
func test_extract_nibble{ range_check_ptr, bitwise_ptr : BitwiseBuiltin* }(word: felt, word_len_bytes: felt, position: felt) -> (res: felt):
    return extract_nibble(word, word_len_bytes, position)
end

@view
func test_extract_nibble_from_words{ range_check_ptr, bitwise_ptr : BitwiseBuiltin* }(words_len: felt, words: felt*, words_len_bytes: felt, position: felt) -> (res: felt):
    let input: IntsSequence = IntsSequence(words, words_len, words_len_bytes)
    return extract_nibble_from_words(input, position)
end
