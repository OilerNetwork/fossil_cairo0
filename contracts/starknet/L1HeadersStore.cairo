%lang starknet
%builtins pedersen range_check ecdsa bitwise

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.cairo_builtins import BitwiseBuiltin
from starkware.starknet.common.syscalls import get_caller_address
from starkware.cairo.common.alloc import alloc

from starknet.types import (Keccak256Hash, Address, IntsSequence)
from starknet.lib.keccak import keccak256
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

from starknet.lib.bitset import bitset_get

# Temporary auth var for authenticating mocked L1 handlers
@storage_var
func _l1_messages_origin() -> (res: felt):
end

# Indicates that the contract has been initialized
@storage_var
func _initialized() -> (res: felt):
end

####################################################
#                 PER BLOCK STORAGE
####################################################

@storage_var
func _block_parent_hash(block_number: felt) -> (res: Keccak256Hash):
end

@storage_var
func _block_state_root(block_number: felt) -> (res: Keccak256Hash):
end

@storage_var
func _block_transactions_root(block_number: felt) -> (res: Keccak256Hash):
end

@storage_var
func _block_receipts_root(block_number: felt) -> (res: Keccak256Hash):
end

@storage_var
func _block_uncles_hash(block_number: felt) -> (res: Keccak256Hash):
end

@storage_var
func _block_beneficiary(block_number: felt) -> (res: Address):
end

@storage_var
func _block_difficulty(block_number: felt) -> (res: felt):
end

@storage_var
func _block_base_fee(block_number: felt) -> (res: felt):
end

@storage_var
func _block_timestamp(block_number: felt) -> (res: felt):
end

@storage_var
func _block_gas_used(block_number: felt) -> (res: felt):
end

####################################################
#                   VIEW FUNCTIONS
####################################################

@view
func get_parent_hash{
        syscall_ptr: felt*,
        pedersen_ptr: HashBuiltin*,
        range_check_ptr
    } (block_number: felt) -> (res: Keccak256Hash):
    return _block_parent_hash.read(block_number)
end

@view
func get_state_root{
        syscall_ptr: felt*,
        pedersen_ptr: HashBuiltin*,
        range_check_ptr
    } (block_number: felt) -> (res: Keccak256Hash):
    return _block_state_root.read(block_number)
end

@view
func get_transactions_root{
        syscall_ptr: felt*,
        pedersen_ptr: HashBuiltin*,
        range_check_ptr
    } (block_number: felt) -> (res: Keccak256Hash):
    return _block_transactions_root.read(block_number)
end

@view
func get_receipts_root{
        syscall_ptr: felt*,
        pedersen_ptr: HashBuiltin*,
        range_check_ptr
    } (block_number: felt) -> (res: Keccak256Hash):
    return _block_receipts_root.read(block_number)
end

@view
func get_uncles_hash{
        syscall_ptr: felt*,
        pedersen_ptr: HashBuiltin*,
        range_check_ptr
    } (block_number: felt) -> (res: Keccak256Hash):
    return _block_uncles_hash.read(block_number)
end

@view
func get_beneficiary{
        syscall_ptr: felt*,
        pedersen_ptr: HashBuiltin*,
        range_check_ptr
    } (block_number: felt) -> (res: Address):
    return _block_beneficiary.read(block_number)
end

@view
func get_difficulty{
        syscall_ptr: felt*,
        pedersen_ptr: HashBuiltin*,
        range_check_ptr
    } (block_number: felt) -> (res: felt):
    return _block_difficulty.read(block_number)
end

@view
func get_base_fee{
        syscall_ptr: felt*,
        pedersen_ptr: HashBuiltin*,
        range_check_ptr
    } (block_number: felt) -> (res: felt):
    return _block_base_fee.read(block_number)
end

@view
func get_timestamp{
        syscall_ptr: felt*,
        pedersen_ptr: HashBuiltin*,
        range_check_ptr
    } (block_number: felt) -> (res: felt):
    return _block_timestamp.read(block_number)
end

@view
func get_gas_used{
        syscall_ptr: felt*,
        pedersen_ptr: HashBuiltin*,
        range_check_ptr
    } (block_number: felt) -> (res: felt):
    return _block_gas_used.read(block_number)
end

@external
func initialize{
        pedersen_ptr: HashBuiltin*,
        syscall_ptr: felt*,
        range_check_ptr
    } (l1_messages_origin: felt):
    let (initialized) = _initialized.read()
    assert initialized = 0
    _initialized.write(1)
    _l1_messages_origin.write(l1_messages_origin)
    return ()
end

@external
func receive_from_l1{
        pedersen_ptr: HashBuiltin*,
        syscall_ptr: felt*,
        range_check_ptr
    } (parent_hash_len: felt, parent_hash: felt*, block_number: felt):
    alloc_locals

    # Auth
    let (caller) = get_caller_address()
    let (l1_messages_origin) = _l1_messages_origin.read()
    assert caller = l1_messages_origin

    # Save block's parenthash
    local hash: Keccak256Hash = Keccak256Hash(
        word_1=parent_hash[0],
        word_2=parent_hash[1],
        word_3=parent_hash[2],
        word_4=parent_hash[3]
    )
    _block_parent_hash.write(block_number, hash)
    return ()
end


# options_set: indicates which element of the block header should be saved in state
# options_set: is a felt in range 0 to 63
# options_set: state_root will be saved if 1st bit of the arg is positive
# options_set: transactions_root will be saved if 2nd bit of the arg is positive
# options_set: receipts_root will be saved if 3rd bit of the arg is positive
# options_set: uncles_hash will be saved if 4th bit of the arg is positive
# options_set: difficulty will be saved if 5th bit of the arg is positive
# options_set: beneficiary will be saved if 6th bit of the arg is positive
# options_set: base_fee will be saved if 7th bit of the arg is positive
# options_set: timestamp will be saved if 8th bit of the arg is positive
# options_set: gas_used will be saved if 9th bit of the arg is positive
@external
func process_block{
        pedersen_ptr: HashBuiltin*,
        syscall_ptr: felt*,
        bitwise_ptr : BitwiseBuiltin*,
        range_check_ptr
    } (options_set: felt,
       block_header_rlp_bytes_len: felt,
       block_number: felt,
       block_header_rlp_len: felt,
       block_header_rlp: felt*
    ):
    alloc_locals
    validate_provided_header_rlp(
        block_number,
        block_header_rlp_bytes_len,
        block_header_rlp_len,
        block_header_rlp)

    local rlp: IntsSequence = IntsSequence(block_header_rlp, block_header_rlp_len, block_header_rlp_bytes_len)

    let (local parent_hash: Keccak256Hash) = decode_parent_hash(rlp)
    _block_parent_hash.write(block_number, parent_hash)

    # Check whether state root should be saved
    let (local save_state_root) = bitset_get(options_set, 1, 9)
    if save_state_root == 1:
        let (local state_root: Keccak256Hash) = decode_state_root(rlp)
        _block_state_root.write(block_number, state_root)
        tempvar syscall_ptr = syscall_ptr
        tempvar range_check_ptr = range_check_ptr
        tempvar pedersen_ptr = pedersen_ptr
    else:
        tempvar syscall_ptr = syscall_ptr
        tempvar range_check_ptr = range_check_ptr
        tempvar pedersen_ptr = pedersen_ptr
    end
    local syscall_ptr : felt* = syscall_ptr
    local range_check_ptr : felt = range_check_ptr
    local pedersen_ptr : HashBuiltin* = pedersen_ptr

    # Check whether transactions root should be saved
    let (local save_txns_root) = bitset_get(options_set, 2, 9)
    if save_txns_root == 1:
        let (local transactions_root: Keccak256Hash) = decode_transactions_root(rlp)
        _block_transactions_root.write(block_number, transactions_root)
        tempvar syscall_ptr = syscall_ptr
        tempvar range_check_ptr = range_check_ptr
        tempvar pedersen_ptr = pedersen_ptr
    else:
        tempvar syscall_ptr = syscall_ptr
        tempvar range_check_ptr = range_check_ptr
        tempvar pedersen_ptr = pedersen_ptr
    end
    local syscall_ptr : felt* = syscall_ptr
    local range_check_ptr : felt = range_check_ptr
    local pedersen_ptr : HashBuiltin* = pedersen_ptr

    # Check whether receipts root should be saved
    let (local save_receipts_root) = bitset_get(options_set, 3, 9)
    if save_receipts_root == 1:
        let (local receipts_root: Keccak256Hash) = decode_receipts_root(rlp)
        _block_receipts_root.write(block_number, receipts_root)
        tempvar syscall_ptr = syscall_ptr
        tempvar range_check_ptr = range_check_ptr
        tempvar pedersen_ptr = pedersen_ptr
    else:
        tempvar syscall_ptr = syscall_ptr
        tempvar range_check_ptr = range_check_ptr
        tempvar pedersen_ptr = pedersen_ptr
    end
    local syscall_ptr : felt* = syscall_ptr
    local range_check_ptr : felt = range_check_ptr
    local pedersen_ptr : HashBuiltin* = pedersen_ptr

    # Check whether uncles hash should be saved
    let (local save_uncles_hash) = bitset_get(options_set, 4, 9)
    if save_uncles_hash == 1:
        let (local uncles_hash: Keccak256Hash) = decode_uncles_hash(rlp)
        _block_uncles_hash.write(block_number, uncles_hash)
        tempvar syscall_ptr = syscall_ptr
        tempvar range_check_ptr = range_check_ptr
        tempvar pedersen_ptr = pedersen_ptr
    else:
        tempvar syscall_ptr = syscall_ptr
        tempvar range_check_ptr = range_check_ptr
        tempvar pedersen_ptr = pedersen_ptr
    end
    local syscall_ptr : felt* = syscall_ptr
    local range_check_ptr : felt = range_check_ptr
    local pedersen_ptr : HashBuiltin* = pedersen_ptr

    # Check whether difficulty should be saved
    let (local save_difficulty) = bitset_get(options_set, 5, 9)
    if save_difficulty == 1:
        let (local difficulty: felt) = decode_difficulty(rlp)
        _block_difficulty.write(block_number, difficulty)
        tempvar syscall_ptr = syscall_ptr
        tempvar range_check_ptr = range_check_ptr
        tempvar pedersen_ptr = pedersen_ptr
    else:
        tempvar syscall_ptr = syscall_ptr
        tempvar range_check_ptr = range_check_ptr
        tempvar pedersen_ptr = pedersen_ptr
    end
    local syscall_ptr : felt* = syscall_ptr
    local range_check_ptr : felt = range_check_ptr
    local pedersen_ptr : HashBuiltin* = pedersen_ptr

    # Check whether beneficiary should be saved
    let (local save_beneficiary) = bitset_get(options_set, 6, 9)
    if save_beneficiary == 1:
        let (local beneficiary: Address) = decode_beneficiary(rlp)
        _block_beneficiary.write(block_number, beneficiary)
        tempvar syscall_ptr = syscall_ptr
        tempvar range_check_ptr = range_check_ptr
        tempvar pedersen_ptr = pedersen_ptr
    else:
        tempvar syscall_ptr = syscall_ptr
        tempvar range_check_ptr = range_check_ptr
        tempvar pedersen_ptr = pedersen_ptr
    end
    local syscall_ptr : felt* = syscall_ptr
    local range_check_ptr : felt = range_check_ptr
    local pedersen_ptr : HashBuiltin* = pedersen_ptr

    # Check whether base fee should be saved
    let (local save_base_fee) = bitset_get(options_set, 7, 9)
    if save_base_fee == 1:
        let (local base_fee: felt) = decode_base_fee(rlp)
        _block_base_fee.write(block_number, base_fee)
        tempvar syscall_ptr = syscall_ptr
        tempvar range_check_ptr = range_check_ptr
        tempvar pedersen_ptr = pedersen_ptr
    else:
        tempvar syscall_ptr = syscall_ptr
        tempvar range_check_ptr = range_check_ptr
        tempvar pedersen_ptr = pedersen_ptr
    end
    local syscall_ptr : felt* = syscall_ptr
    local range_check_ptr : felt = range_check_ptr
    local pedersen_ptr : HashBuiltin* = pedersen_ptr

    # Check whether timestamp should be saved
    let (local save_timestamp) = bitset_get(options_set, 8, 9)
    if save_timestamp == 1:
        let (local timestamp: felt) = decode_timestamp(rlp)
        _block_timestamp.write(block_number, timestamp)
        tempvar syscall_ptr = syscall_ptr
        tempvar range_check_ptr = range_check_ptr
        tempvar pedersen_ptr = pedersen_ptr
    else:
        tempvar syscall_ptr = syscall_ptr
        tempvar range_check_ptr = range_check_ptr
        tempvar pedersen_ptr = pedersen_ptr
    end
    local syscall_ptr : felt* = syscall_ptr
    local range_check_ptr : felt = range_check_ptr
    local pedersen_ptr : HashBuiltin* = pedersen_ptr

    # Check whether gas used should be saved
    let (local save_gas_used) = bitset_get(options_set, 9, 9)
    if save_gas_used == 1:
        let (local gas_used: felt) = decode_gas_used(rlp)
        _block_gas_used.write(block_number, gas_used)
        tempvar syscall_ptr = syscall_ptr
        tempvar range_check_ptr = range_check_ptr
        tempvar pedersen_ptr = pedersen_ptr
    else:
        tempvar syscall_ptr = syscall_ptr
        tempvar range_check_ptr = range_check_ptr
        tempvar pedersen_ptr = pedersen_ptr
    end

    return ()
end

func validate_provided_header_rlp{
        pedersen_ptr: HashBuiltin*,
        syscall_ptr: felt*,
        bitwise_ptr : BitwiseBuiltin*,
        range_check_ptr
    } (block_number: felt,
       block_header_rlp_bytes_len: felt,
       block_header_rlp_len: felt,
       block_header_rlp: felt*
    ):
    alloc_locals
    local bitwise_ptr: BitwiseBuiltin* = bitwise_ptr
    let (local keccak_ptr : felt*) = alloc()
    let keccak_ptr_start = keccak_ptr

    let child_block_number = (block_number + 1)
    let (local child_block_parent: Keccak256Hash) = _block_parent_hash.read(block_number=child_block_number)

    let (provided_rlp_hash) = keccak256{keccak_ptr=keccak_ptr}(block_header_rlp, block_header_rlp_bytes_len)

    # Ensure child block parenthash matches provided rlp hash
    assert child_block_parent.word_1 = provided_rlp_hash[0]
    assert child_block_parent.word_2 = provided_rlp_hash[1]
    assert child_block_parent.word_3 = provided_rlp_hash[2]
    assert child_block_parent.word_4 = provided_rlp_hash[3]
    return ()
end
