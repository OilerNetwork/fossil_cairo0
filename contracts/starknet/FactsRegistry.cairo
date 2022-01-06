%lang starknet
%builtins pedersen range_check ecdsa bitwise

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.cairo_builtins import BitwiseBuiltin
from starkware.cairo.common.alloc import alloc

from starknet.types import (Keccak256Hash, Address)
from starknet.lib.keccak import keccak256
from starknet.lib.extract_from_rlp import IntsSequence

# L1HeadersStore simplified interface
@contract_interface
namespace IL1HeadersStore:
    func get_parent_hash(block_number: felt) -> (res: Keccak256Hash):
    end

    func get_state_root(block_number: felt) -> (res: Keccak256Hash):
    end

    func get_transactions_root(block_number: felt) -> (res: Keccak256Hash):
    end

    func get_receipts_root(block_number: felt) -> (res: Keccak256Hash):
    end

    func get_uncles_hash(block_number: felt) -> (res: Keccak256Hash):
    end
end

@storage_var
func _verified_account_storage_hash(account: felt, block: felt) -> (res: Keccak256Hash):
end

@storage_var
func _verified_account_code_hash(account: felt, block: felt) -> (res: Keccak256Hash):
end

@storage_var
func _verified_account_balance(account: felt, block: felt) -> (res: felt):
end

@storage_var
func _verified_account_nonce(account: felt, block: felt) -> (res: felt):
end

# options_map: indicates which element of the decoded proof should be saved in state
# options_map: is a felt in range 0 to 16
# options_map: storage_hash will be saved if 1st bit of the arg is positive
# options_map: code_hash will be saved if 2nd bit of the arg is positive
# options_map: nonce will be saved if 3rd bit of the arg is positive
# options_map: balance will be saved if 4th bit of the arg is positive
@external
func prove_account{ range_check_ptr, bitwise_ptr : BitwiseBuiltin* }(
    account: Address,
    proof_sizes_bytes_len: felt,
    proof_sizes_bytes: felt*,
    proof_sizes_words_len: felt,
    proof_sizes_words: felt*,
    proofs_concat_len: felt,
    proofs_concat: felt*):
    alloc_locals
    let (local account_raw) = alloc()
    assert account_raw[0] = account.word_1
    assert account_raw[1] = account.word_2
    assert account_raw[2] = account.word_3

    let (local keccak_ptr : felt*) = alloc()
    let keccak_ptr_start = keccak_ptr
    let (local path_raw) = keccak256{keccak_ptr=keccak_ptr}(account_raw, 20)

    local path: IntsSequence = IntsSequence(path_raw, 4, 32)
    return ()
end