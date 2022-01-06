%lang starknet
%builtins pedersen range_check ecdsa bitwise

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.cairo_builtins import BitwiseBuiltin

from starknet.types import (Keccak256Hash, Address)

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