%lang starknet
%builtins pedersen range_check ecdsa bitwise

from starknet.types import IntsSequence
from starknet.lib.words64 import extract_nibble, extract_nibble_from_words, to_words128

@view
func test_extract_nibble{ range_check_ptr }(word: felt, word_len_bytes: felt, position: felt) -> (res: felt):
    return extract_nibble(word, word_len_bytes, position)
end

@view
func test_extract_nibble_from_words{ range_check_ptr }(words_len: felt, words: felt*, words_len_bytes: felt, position: felt) -> (res: felt):
    alloc_locals
    let input: IntsSequence = IntsSequence(words, words_len, words_len_bytes)
    let (local result) = extract_nibble_from_words(input, position)
    return (result)
end

@view
func test_to_words128{ range_check_ptr }(words64_len_bytes: felt, words64_len: felt, words64: felt*) -> (res_len: felt, res: felt*):
    alloc_locals
    local input: IntsSequence = IntsSequence(words64, words64_len, words64_len_bytes)
    let (local words128: felt*, local words128_len: felt) = to_words128(input)
    return (words128_len, words128)
end
