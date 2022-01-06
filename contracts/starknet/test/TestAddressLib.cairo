%lang starknet
%builtins pedersen range_check ecdsa

from starknet.lib.address import address_words64_to_160bit, address_160bit_to_words64
from starknet.types import Address

@view
func test_address_words64_to_160bit{ range_check_ptr }(
    word_1: felt,
    word_2: felt,
    word_3: felt) -> (res: felt):
    alloc_locals
    local input: Address = Address(word_1, word_2, word_3)
    return address_words64_to_160bit(input)
end

@view
func test_address_160bit_to_words64{ range_check_ptr }(input: felt) -> (res: Address):
    return address_160bit_to_words64(input)
end