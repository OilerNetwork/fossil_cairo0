%lang starknet
%builtins pedersen range_check ecdsa bitwise

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.cairo_builtins import BitwiseBuiltin
from starkware.cairo.common.alloc import alloc

from starknet.lib.unsafe_keccak import keccak256
from starknet.types import IntsSequence, Keccak256Hash

@view
func test_unsafe_keccak256{range_check_ptr, bitwise_ptr : BitwiseBuiltin*}(keccak_input_length: felt, input_len: felt, input: felt*) -> (res: Keccak256Hash):
    alloc_locals
    let (local keccak_ptr : felt*) = alloc()
    let keccak_ptr_start = keccak_ptr

    local keccak_input: IntsSequence = IntsSequence(input, input_len, keccak_input_length)

    let (keccak_hash) = keccak256{keccak_ptr=keccak_ptr}(keccak_input)

    local hash: Keccak256Hash = Keccak256Hash(
        word_1=keccak_hash[0],
        word_2=keccak_hash[1],
        word_3=keccak_hash[2],
        word_4=keccak_hash[3]
    )

    return (hash)
end