%lang starknet
%builtins pedersen range_check ecdsa bitwise

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.cairo_builtins import BitwiseBuiltin
from starkware.starknet.common.syscalls import get_caller_address
from starkware.cairo.common.alloc import alloc
from starkware.cairo.common.hash_chain import hash_chain
from starkware.cairo.common.hash import hash2
from starkware.cairo.common.math import assert_not_zero, assert_le, unsigned_div_rem
from starkware.cairo.common.math_cmp import is_le

from starknet.types import (Keccak256Hash, IntsSequence, slice_arr)
from starknet.lib.unsafe_keccak import keccak256
from starknet.lib.blockheader_rlp_extractor import (
    decode_parent_hash,
    decode_state_root,
    decode_transactions_root,
    decode_receipts_root,
    decode_difficulty,
    decode_beneficiary,
    decode_uncles_hash,
    decode_base_fee,
    decode_timestamp,
    decode_gas_used
)

@contract_interface
namespace IL1HeadersStore:
    func get_parent_hash(block_number : felt) -> (res : Keccak256Hash):
    end
end

@contract_interface
namespace CallbackReceiver:
    func twap_callback(res: felt):
    end
end

@storage_var
func _initialized() -> (res: felt):
end

@storage_var
func _l1_headers_store_addr() -> (res: felt):
end

@storage_var
func _twap_computation_cache(computation_id: felt, slot: felt) -> (res: felt):
end

@external
func initialize{
        pedersen_ptr: HashBuiltin*,
        syscall_ptr: felt*,
        range_check_ptr
    } (l1_headers_store_addr: felt):
    let (initialized) = _initialized.read()
    assert initialized = 0
    _initialized.write(1)
    _l1_headers_store_addr.write(l1_headers_store_addr)
    return ()
end

# upper bound e.g. 1100
# lower bound e.g. 1000
# index of the param in the header to be avg e.g. 15 (basefee)
@external
func register_computation{
        pedersen_ptr: HashBuiltin*,
        syscall_ptr: felt*,
        range_check_ptr
    } (start_block: felt,
       end_block: felt,
       avg_header_param: felt,
       callback_address: felt):
    alloc_locals

    assert_le(end_block, start_block - 1)

    let (local tmp_1) = hash2{hash_ptr=pedersen_ptr}(start_block, end_block)
    let (local tmp_2) = hash2{hash_ptr=pedersen_ptr}(tmp_1, callback_address)
    let (local computation_id) = hash2{hash_ptr=pedersen_ptr}(tmp_2, avg_header_param)

    let (local computation_already_registered) = _twap_computation_cache.read(computation_id, 0)
    assert computation_already_registered = 0

    let (local l1_headers_store_addr) = _l1_headers_store_addr.read()
    let (local current_block_hash) = IL1HeadersStore.get_parent_hash(l1_headers_store_addr, start_block + 1)

   assert_not_zero(current_block_hash.word_1)
   assert_not_zero(current_block_hash.word_2)
   assert_not_zero(current_block_hash.word_3)
   assert_not_zero(current_block_hash.word_4)

    # Fill cache metadata
    _twap_computation_cache.write(computation_id, 0, start_block)
    _twap_computation_cache.write(computation_id, 1, end_block)
    _twap_computation_cache.write(computation_id, 2, start_block)
    _twap_computation_cache.write(computation_id, 3, current_block_hash.word_1)
    _twap_computation_cache.write(computation_id, 4, current_block_hash.word_2)
    _twap_computation_cache.write(computation_id, 5, current_block_hash.word_3)
    _twap_computation_cache.write(computation_id, 6, current_block_hash.word_4)
    _twap_computation_cache.write(computation_id, 7, callback_address)
    _twap_computation_cache.write(computation_id, 8, avg_header_param)
    _twap_computation_cache.write(computation_id, 9, 0)
    _twap_computation_cache.write(computation_id, 10, 0)
    return ()
end

@external
func compute{
        pedersen_ptr: HashBuiltin*,
        syscall_ptr: felt*,
        bitwise_ptr : BitwiseBuiltin*,
        range_check_ptr
    } (computation_id: felt,
       block_headers_lens_bytes_len: felt,
       block_headers_lens_bytes: felt*,
       block_headers_lens_words_len: felt,
       block_headers_lens_words: felt*,
       block_headers_concat_len: felt,
       block_headers_concat: felt*
    ):
    alloc_locals

    let (local val_acc) = _twap_computation_cache.read(computation_id, 9)
    let (local val_len) = _twap_computation_cache.read(computation_id, 10)
    let (local end_block) = _twap_computation_cache.read(computation_id, 1)
    let (local current_block) = _twap_computation_cache.read(computation_id, 2)
    let (local avg_header_param) = _twap_computation_cache.read(computation_id, 8)
    let (local current_block_hash_word_1) = _twap_computation_cache.read(computation_id, 3)
    let (local current_block_hash_word_2) = _twap_computation_cache.read(computation_id, 4)
    let (local current_block_hash_word_3) = _twap_computation_cache.read(computation_id, 5)
    let (local current_block_hash_word_4) = _twap_computation_cache.read(computation_id, 6)

    assert_not_zero(current_block_hash_word_1)
    assert_not_zero(current_block_hash_word_2)
    assert_not_zero(current_block_hash_word_3)
    assert_not_zero(current_block_hash_word_4)

    local current_block_hash: Keccak256Hash = Keccak256Hash(
        current_block_hash_word_1,
        current_block_hash_word_2,
        current_block_hash_word_3,
        current_block_hash_word_4)

    let (
        local last_block_number: felt,
        local last_hash: Keccak256Hash,
        local param_acc: felt,
        local iterations: felt) = compute_rec(
            avg_header_param,
            current_block,
            current_block_hash,
            block_headers_lens_bytes_len,
            block_headers_lens_bytes,
            block_headers_lens_words_len,
            block_headers_lens_words,
            block_headers_concat_len,
            block_headers_concat,
            0,
            0,
            0)

    let (local is_population_full) = is_le(last_block_number, end_block)
    
    if is_population_full == 1:
        let (local twap, _) = unsigned_div_rem(val_acc + param_acc, val_len + iterations)
        let (local callback_receiver) = _twap_computation_cache.read(computation_id, 7)

        _twap_computation_cache.write(computation_id, 0, 0)
        _twap_computation_cache.write(computation_id, 1, 0)
        _twap_computation_cache.write(computation_id, 2, 0)
        _twap_computation_cache.write(computation_id, 3, 0)
        _twap_computation_cache.write(computation_id, 4, 0)
        _twap_computation_cache.write(computation_id, 5, 0)
        _twap_computation_cache.write(computation_id, 6, 0)
        _twap_computation_cache.write(computation_id, 7, 0)
        _twap_computation_cache.write(computation_id, 8, 0)
        _twap_computation_cache.write(computation_id, 9, 0)
        _twap_computation_cache.write(computation_id, 10, 0)
        CallbackReceiver.twap_callback(callback_receiver, twap)
        return ()
    else:
        _twap_computation_cache.write(computation_id, 9, val_acc + param_acc)
        _twap_computation_cache.write(computation_id, 10, val_len + iterations)
        _twap_computation_cache.write(computation_id, 1, last_block_number)

        _twap_computation_cache.write(computation_id, 3, last_hash.word_1)
        _twap_computation_cache.write(computation_id, 4, last_hash.word_2)
        _twap_computation_cache.write(computation_id, 5, last_hash.word_3)
        _twap_computation_cache.write(computation_id, 6, last_hash.word_4)
        return ()
    end
    ret
end

func compute_rec{
        pedersen_ptr: HashBuiltin*,
        syscall_ptr: felt*,
        bitwise_ptr : BitwiseBuiltin*,
        range_check_ptr
    } (avg_header_param: felt,
       start_block_number: felt,
       current_parent_hash: Keccak256Hash,
       block_headers_lens_bytes_len: felt,
       block_headers_lens_bytes: felt*,
       block_headers_lens_words_len: felt,
       block_headers_lens_words: felt*,
       block_headers_concat_len: felt,
       block_headers_concat: felt*,
       param_acc: felt,
       current_index: felt,
       offset: felt
    ) -> (last_block_number: felt, last_hash: Keccak256Hash, param_acc: felt, iterations: felt):
    alloc_locals
    # Skips last header as this will be processed by process_block
    if current_index == block_headers_lens_bytes_len:
        return (start_block_number - current_index, current_parent_hash, param_acc, current_index)
    end

    let (local current_header: felt*) = alloc()
    let (offset_updated) = slice_arr(
        offset,
        block_headers_lens_words[current_index],
        block_headers_concat,
        block_headers_concat_len,
        current_header,
        0,
        0)
    
    local bitwise_ptr: BitwiseBuiltin* = bitwise_ptr
    let (local keccak_ptr : felt*) = alloc()
    let keccak_ptr_start = keccak_ptr

    local current_header_ints_sequence: IntsSequence = IntsSequence(current_header, block_headers_lens_words[current_index], block_headers_lens_bytes[current_index])
    
    let (provided_rlp_hash) = keccak256{keccak_ptr=keccak_ptr}(current_header_ints_sequence)

    assert current_parent_hash.word_1 = provided_rlp_hash[0]
    assert current_parent_hash.word_2 = provided_rlp_hash[1]
    assert current_parent_hash.word_3 = provided_rlp_hash[2]
    assert current_parent_hash.word_4 = provided_rlp_hash[3]

    local current_header_rlp: IntsSequence = IntsSequence(current_header, block_headers_lens_words[current_index], block_headers_lens_bytes[current_index])
    let (local parent_hash: Keccak256Hash) = decode_parent_hash(current_header_rlp)

    let (local param) = retrieve_param(current_header_rlp, avg_header_param)

    return compute_rec(
        avg_header_param,
        start_block_number,
        parent_hash,
        block_headers_lens_bytes_len,
        block_headers_lens_bytes,
        block_headers_lens_words_len,
        block_headers_lens_words,
        block_headers_concat_len,
        block_headers_concat,
        param_acc + param,
        current_index + 1,
        offset_updated)
end

func retrieve_param{range_check_ptr}(header_rlp: IntsSequence, avg_header_param: felt) -> (res: felt):
    if avg_header_param == 15:
        return decode_base_fee(header_rlp)
    end

    if avg_header_param == 7:
        return decode_difficulty(header_rlp)
    end

    if avg_header_param == 10:
        return decode_gas_used(header_rlp)
    end

    assert 1 = 0
    return (42)
end


# 0 -> start_block
# 1 -> end_block
# 2 -> current_block
# 3 -> current_block_hash
# 4 -> callback address
# 5 -> val index
# 6 -> acc_val
# 7 -> acc_len
