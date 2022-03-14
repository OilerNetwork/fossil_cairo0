%lang starknet
%builtins pedersen range_check bitwise

from starkware.cairo.common.cairo_builtins import BitwiseBuiltin
from starkware.cairo.common.uint256 import Uint256
from starknet.types import IntsSequence 
from starknet.lib.ints_to_uint256 import ints_to_uint256 

from starkware.cairo.common.pow import pow
from starkware.cairo.common.math import unsigned_div_rem
from starkware.cairo.common.math_cmp import is_le

@view 
func test_ints_to_uint256{range_check_ptr, bitwise_ptr : BitwiseBuiltin*}(element_len_bytes: felt, element_len: felt, element: felt*) -> (uint256: Uint256):
    alloc_locals
    local input: IntsSequence = IntsSequence(element, element_len, element_len_bytes)
    let (local out: Uint256) = ints_to_uint256(ints=input)
    return (out)
end
