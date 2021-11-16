from starknet.lib.packed_keccak import BLOCK_SIZE, packed_keccak_func
from starknet.lib.xor_state import state_xor, mask_garbage

from starkware.cairo.common.alloc import alloc
from starkware.cairo.common.cairo_builtins import BitwiseBuiltin
from starkware.cairo.common.math import assert_nn_le, unsigned_div_rem
from starkware.cairo.common.math_cmp import is_le
from starkware.cairo.common.memset import memset
from starkware.cairo.common.pow import pow

# Runs keccak_f permutations on the given input
# Uses packed_keccak_func from Starkware (in native Cairo)
# Then 8 right bytes of each felt are extracted with a mask (everything to the left is considered garbage)
func keccak_f{range_check_ptr, keccak_ptr : felt*, bitwise_ptr : BitwiseBuiltin*}(input : felt*) -> (output : felt*):
    let (garbaged_output) = packed_keccak_func(input)
    let (clean_output) = mask_garbage(garbaged_output)
    return (clean_output)
end

# Loads next keccak256 size block of words of the given inputs
#
# The input here is considered to be 136 bytes, so we can just copy it directly
# The rest is filled with zero's to form a 200byte state
func load_full_block{range_check_ptr, keccak_ptr_start: felt*, keccak_ptr : felt*}(
        input : felt*) -> (formatted_input : felt*):
    alloc_locals

    assert keccak_ptr[0] = input[0]
    assert keccak_ptr[1] = input[1]
    assert keccak_ptr[2] = input[2]
    assert keccak_ptr[3] = input[3]
    assert keccak_ptr[4] = input[4]
    assert keccak_ptr[5] = input[5]
    assert keccak_ptr[6] = input[6]
    assert keccak_ptr[7] = input[7]
    assert keccak_ptr[8] = input[8]
    assert keccak_ptr[9] = input[9]
    assert keccak_ptr[10] = input[10]
    assert keccak_ptr[11] = input[11]
    assert keccak_ptr[12] = input[12]
    assert keccak_ptr[13] = input[13]
    assert keccak_ptr[14] = input[14]
    assert keccak_ptr[15] = input[15]
    assert keccak_ptr[16] = input[16]
    assert keccak_ptr[17] = 0
    assert keccak_ptr[18] = 0
    assert keccak_ptr[19] = 0
    assert keccak_ptr[20] = 0
    assert keccak_ptr[21] = 0
    assert keccak_ptr[22] = 0
    assert keccak_ptr[23] = 0
    assert keccak_ptr[24] = 0
    let keccak_ptr = keccak_ptr + 25

    return (keccak_ptr_start)
end

# Loads next keccak256 size block of words of the given inputs and applies additional padding
#
# In case the input is less than 136 bytes - padding rules must apply:
#   - input = 135bytes - 0x81 is added as a 136th byte (lsb)
#   - input < 135bytes - 0x80 is added as a 136th byte and 0x01 is added after the end of data
#   - if the input is empty - 0x01 is added at the beginning of the block, and 0x80 at 136th position
#
#   the rest is filled with zeroes to form a 200byte state
#
# The function  works recursively on each 64bit word.
# Initially it's fed with n_word = 17, which is an inverse index (for recursion purposes)
# Based on the n_word we can determine current index in the block:
#   - If n_word = 17 it means the current word is the first
#   - If n_word = 1 it means the current word is the last
#   - If n_word = 0 it means we already processed the data in the block and need to add capacity padding zeroes (8 words of them)

func load_block_with_padding{range_check_ptr, keccak_ptr_start: felt*, keccak_ptr : felt*}(
        input : felt*, n_bytes : felt, n_word : felt) -> (formatted_input : felt*):
    alloc_locals

    let (_, is_full_word) = unsigned_div_rem(n_bytes, 8)
    # %{ ids.is_full_word = int(ids.n_bytes >= 8) %}

    # If the current word is full (8 bytes, 64 bits) - we just copy it to the state
    if is_full_word != 0:
        assert keccak_ptr[0] = input[0]
        let keccak_ptr = keccak_ptr + 1
        load_block_with_padding(input=input + 1, n_bytes=n_bytes - 8, n_word=n_word - 1)
        return (keccak_ptr_start)
    # Else, if the word is less than 8 bytes - we consider to add padding
    else:
        local final_padding

        # If it is the last word
        if n_word == 1: 
            assert final_padding = 2 * 2 ** 62 # Add a padding 0x80 00 00 00 00 00 00 00
        else:
            assert final_padding = 0 # No 0x80 padding will be added
        end
        
        assert_nn_le(n_bytes, 7)
        let (padding) = pow(256, n_bytes) # This adds a 0x01 based on how many input bytes are left, straight to the left of them
        local range_check_ptr = range_check_ptr

        # If there are no bytes, then we just add the 0x01 padding to the right (and 0x80 to the left)
        if n_bytes == 0:
            if n_word != 0:
                assert keccak_ptr[0] = 1 + final_padding
            end
        # If there is some input data left in current word, we add 0x01 and 0x80 paddings to the left of the data
        else:
            assert keccak_ptr[0] = input[0] + padding + final_padding
        end

        # If the input data finished at the last word - we add 8 words of capacity zeroes after it (64 bits)
        if n_word == 1:
            memset(dst=keccak_ptr + 1, value=0, n=n_word - 1 + 8)
            let keccak_ptr = keccak_ptr + n_word + 8
            return (keccak_ptr_start)
        # If the input data finished earlier than the 17th word:
        else:
            # Fill with zeroes until the last 17th word
            memset(dst=keccak_ptr + 1, value=0, n=n_word - 2)
            let keccak_ptr = keccak_ptr + n_word - 1
            # Insert a 0x80 00 00 00 00 00 00 00 padding at the 17th word
            assert keccak_ptr[0] = 2 * 2 ** 62
            # Fill the rest 8 words of capacity section with zeroes
            memset(dst=keccak_ptr + 1, value=0, n=8)
            return (keccak_ptr_start)
        end
    end
end

# Recursively runs the keccak256 algorithm, processing the imput block by block
# Block size is fixed as 25 words (1600 bits),
# in which 17 words (1088 bits) represent data
#
# Last block of data is being padded
#
# Each iteration consists of loading/formatting the data for the block
# xorring the block with previous state
# and performind a keccak permutation on that xor
func recursive_keccak{range_check_ptr, keccak_ptr : felt*, bitwise_ptr : BitwiseBuiltin*}(state: felt*, input : felt*, n_bytes : felt) -> (output : felt*):
    alloc_locals
    let (is_n_bytes_above_136) = is_le(136, n_bytes)
    local n_bytes_in_current_block
    if is_n_bytes_above_136 == 0:
        assert n_bytes_in_current_block = 136
    else:
        assert n_bytes_in_current_block = n_bytes
    end
    
    # If current input block is full (136 bytes, 1088 bits) - we use an optimized loader 
    if n_bytes_in_current_block == 136:
        let (formatted_input: felt *) = load_full_block{keccak_ptr_start=keccak_ptr}(input=input)
        let (xor: felt*) = state_xor(state, formatted_input)
        let (keccak_f_ptr: felt*) = keccak_f(input=xor)
        let (state_update: felt*) = recursive_keccak(state=keccak_f_ptr, input=input+17, n_bytes=n_bytes-n_bytes_in_current_block)
        return (state_update)
    # For any block that is less than 136 bytes - the data is padded by keccak256 standard.
    # In case all previous blocks were perfectly 136 bytes - the last iteration should be perfomed on an empty block, also padded
    else:
        let (formatted_input: felt *) = load_block_with_padding{keccak_ptr_start=keccak_ptr}(input=input, n_bytes=n_bytes_in_current_block, n_word=17)
        let (xor: felt*) = state_xor(state, formatted_input)
        let (keccak_f_ptr: felt*) = keccak_f(input=xor)
        return (keccak_f_ptr)
    end
end


# Computes the keccak256 of 'input'. Inputs of any size are supported.
# To use this function, split the input into words of 64 bits (little endian).
# For example, to compute keccak('Hello world!'), use:
#   input = [8031924123371070792, 560229490]
# where:
#   8031924123371070792 == int.from_bytes(b'Hello wo', 'little')
#   560229490 == int.from_bytes(b'rld!', 'little')
#
# output is an array of 4 64-bit words (little endian).
#
#
func keccak256{range_check_ptr, keccak_ptr : felt*, bitwise_ptr : BitwiseBuiltin*}(input : felt*, n_bytes : felt) -> (output : felt*):
    let keccak_ptr_start = keccak_ptr
    alloc_locals

    # Allocates an empty felt array which will represent initial zeroed state
    let (local state : felt*) = alloc()

    # Fill state with 25 zeros
    assert state[0] = 0
    assert state[1] = 0
    assert state[2] = 0
    assert state[3] = 0
    assert state[4] = 0
    assert state[5] = 0
    assert state[6] = 0
    assert state[7] = 0
    assert state[8] = 0
    assert state[9] = 0
    assert state[10] = 0
    assert state[11] = 0
    assert state[12] = 0
    assert state[13] = 0
    assert state[14] = 0
    assert state[15] = 0
    assert state[16] = 0
    assert state[17] = 0
    assert state[18] = 0
    assert state[19] = 0
    assert state[20] = 0
    assert state[21] = 0
    assert state[22] = 0
    assert state[23] = 0
    assert state[24] = 0

    # Run keccak recursively
    let (output: felt*) = recursive_keccak(state=state, input=input, n_bytes=n_bytes)
    return (output)
end
