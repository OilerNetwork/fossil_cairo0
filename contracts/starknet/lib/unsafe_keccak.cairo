from starkware.cairo.common.keccak import unsafe_keccak
from starkware.cairo.common.alloc import alloc
from starkware.cairo.common.cairo_builtins import BitwiseBuiltin
from starkware.cairo.common.uint256 import split_64


from starknet.lib.words64 import to_words128
from starknet.types import IntsSequence

func keccak256{range_check_ptr, keccak_ptr : felt*, bitwise_ptr : BitwiseBuiltin*}(input : IntsSequence) -> (output : felt*):
    alloc_locals
    let (local input_words128, local input_words128_len) = to_words128(input)

    local last_word = input_words128[input_words128_len - 1]
    let (local high, local low) = unsafe_keccak(input_words128, input.element_size_bytes)

    let (local word2, local word1) = split_64(low)
    let (local word4, local word3) = split_64(high)

    let (local res) = alloc()
    assert res[0] = word1
    assert res[1] = word2
    assert res[2] = word3
    assert res[3] = word4
    return (res)
end
