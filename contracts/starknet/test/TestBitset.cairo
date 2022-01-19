%lang starknet
%builtins pedersen range_check ecdsa

from starknet.lib.bitset import (bitset4_get, bitset6_get)

@view
func test_bitset4_get{ range_check_ptr }(bitset: felt, position: felt) -> (res: felt):
    return bitset4_get(bitset, position)
end

@view
func test_bitset6_get{ range_check_ptr }(bitset: felt, position: felt) -> (res: felt):
    return bitset6_get(bitset, position)
end