%lang starknet
%builtins pedersen range_check ecdsa

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.starknet.common.syscalls import get_caller_address
from starkware.cairo.common.alloc import alloc


# L1HeadersStore simplified interface
@contract_interface
namespace IL1HeadersStore:
    func receive_from_l1 (parent_hash_len: felt, parent_hash: felt*, block_number: felt):
    end
end

# L1 address allowed to send messages to this contract 
@storage_var
func _l1_messages_sender() -> (res: felt):
end

# Starknet address of the he
@storage_var
func _l1_headers_store_addr() -> (res: felt):
end

# Contract owner
@storage_var
func _owner() -> (res: felt):
end

# Indicates if contract has already been initialized
@storage_var
func _initialized() -> (res: felt):
end

####################################################
#                   VIEW FUNCTIONS
####################################################

@view
func get_l1_messages_sender{
        syscall_ptr: felt*,
        pedersen_ptr: HashBuiltin*,
        range_check_ptr
    } () -> (res: felt):
    return _l1_messages_sender.read()
end

@view
func get_l1_headers_store_addr{
        syscall_ptr: felt*,
        pedersen_ptr: HashBuiltin*,
        range_check_ptr
    } () -> (res: felt):
    return _l1_headers_store_addr.read()
end

@view
func get_owner{
        syscall_ptr: felt*,
        pedersen_ptr: HashBuiltin*,
        range_check_ptr
    } () -> (res: felt):
    return _owner.read()
end

# Initializes the contract
@external
func initialize{
        pedersen_ptr: HashBuiltin*,
        syscall_ptr: felt*,
        range_check_ptr
    } (l1_messages_sender: felt, l1_headers_store_addr: felt, owner: felt):
    let (initialized) = _initialized.read()
    assert initialized = 0
    _initialized.write(1)
    _l1_messages_sender.write(l1_messages_sender)
    _l1_headers_store_addr.write(l1_headers_store_addr)
    _owner.write(owner)
    return ()
end

@external 
func change_owner{
        pedersen_ptr: HashBuiltin*,
        syscall_ptr: felt*,
        range_check_ptr
    } (new_owner: felt):
    let (caller) = get_caller_address()
    let (current_owner) = _owner.read()

    assert caller = current_owner
    _owner.write(new_owner)
    return ()
end

@external
func change_contract_addresses{
        pedersen_ptr: HashBuiltin*,
        syscall_ptr: felt*,
        range_check_ptr
    } (new_sender_addr: felt, new_headers_store_addr: felt):
    let (caller) = get_caller_address()
    let (current_owner) = _owner.read()

    assert caller = current_owner

    _l1_messages_sender.write(new_sender_addr)
    _l1_headers_store_addr.write(new_headers_store_addr)
    return ()
end

@l1_handler
func receive_from_l1{
        pedersen_ptr: HashBuiltin*,
        syscall_ptr: felt*,
        range_check_ptr
    } (from_address : felt,
       parent_hash_word_1: felt,
       parent_hash_word_2: felt,
       parent_hash_word_3: felt,
       parent_hash_word_4: felt,
       block_number: felt):
    alloc_locals
    let (l1_sender) = _l1_messages_sender.read()
    assert from_address = l1_sender

    let (contract_addr) = _l1_headers_store_addr.read()

    let (local parent_hash: felt*) = alloc()

    assert parent_hash[0] = parent_hash_word_1
    assert parent_hash[1] = parent_hash_word_2
    assert parent_hash[2] = parent_hash_word_3
    assert parent_hash[3] = parent_hash_word_4

    IL1HeadersStore.receive_from_l1(contract_address=contract_addr, parent_hash_len=4, parent_hash=parent_hash, block_number=block_number)
    return ()
end

