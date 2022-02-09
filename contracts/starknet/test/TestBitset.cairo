%lang starknet
%builtins pedersen range_check ecdsa

from starknet.lib.bitset import (bitset_get)

@view
func test_bitset_get{ range_check_ptr }(bitset: felt, position: felt) -> (res: felt):
    return bitset_get(bitset, position)
end