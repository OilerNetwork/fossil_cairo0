%lang starknet
%builtins pedersen range_check ecdsa bitwise

from starkware.cairo.common.cairo_builtins import BitwiseBuiltin
from starknet.lib.words64 import extract_nibble

@view
func test_extract_nibble{ range_check_ptr, bitwise_ptr : BitwiseBuiltin* }(word: felt, size: felt) -> (res: felt):
    return extract_nibble(word, size)
end
