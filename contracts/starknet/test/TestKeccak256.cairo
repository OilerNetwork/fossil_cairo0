%lang starknet
%builtins pedersen range_check ecdsa bitwise

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.cairo_builtins import BitwiseBuiltin
from starkware.starknet.common.syscalls import get_caller_address
from starkware.cairo.common.alloc import alloc

from starknet.lib.keccak import keccak256

@view
func test_keccak256{range_check_ptr, bitwise_ptr : BitwiseBuiltin*}(input_len : felt, input : felt*) -> (output_len: felt, output : felt*):
    alloc_locals
    let (local keccak_ptr : felt*) = alloc()
    let keccak_ptr_start = keccak_ptr
    let (keccak_hash) = keccak256{keccak_ptr=keccak_ptr}(input, input_len)
    return (output_len=32, output=keccak_hash)
end