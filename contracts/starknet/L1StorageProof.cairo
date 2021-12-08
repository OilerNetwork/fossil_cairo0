%lang starknet
%builtins pedersen range_check ecdsa bitwise

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.cairo_builtins import BitwiseBuiltin
from starkware.starknet.common.syscalls import get_caller_address
from starkware.cairo.common.alloc import alloc

from starknet.types import (Keccak256Hash, Address)
from starknet.lib.keccak import keccak256
from starknet.lib.blockheader_rlp_extractor import (
    decode_parent_hash,
    decode_state_root,
    decode_transactions_root,
    decode_receipts_root,
    decode_difficulty,
    decode_beneficiary,
    decode_uncles_hash
)


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

# TODO convert to L1 handler once the rest is tested
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

    # Ensure not overwriting. TODO consider if needed due to reorgs on L1
    let (local block_parent_hash: Keccak256Hash) = _block_parent_hash.read(block_number=block_number)
    assert block_parent_hash.word_1 = 0
    assert block_parent_hash.word_2 = 0
    assert block_parent_hash.word_3 = 0
    assert block_parent_hash.word_4 = 0

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

@external
func process_block{
        pedersen_ptr: HashBuiltin*,
        syscall_ptr: felt*,
        bitwise_ptr : BitwiseBuiltin*,
        range_check_ptr
    } (block_header_rlp_words_len: felt,
       block_number: felt,
       block_header_rlp_len: felt,
       block_header_rlp: felt*
    ):
    alloc_locals
    validate_provided_header_rlp(
        block_number,
        block_header_rlp_words_len,
        block_header_rlp_len,
        block_header_rlp)

    # Decode parent hash from rlp
    let (local parent_hash: Keccak256Hash) = decode_parent_hash(block_rlp=block_header_rlp, block_rlp_len=block_header_rlp_len)
    _block_parent_hash.write(block_number, parent_hash)
    return()
end

@external
func set_block_state_root{
        pedersen_ptr: HashBuiltin*,
        syscall_ptr: felt*,
        bitwise_ptr : BitwiseBuiltin*,
        range_check_ptr
    } (block_header_rlp_words_len: felt,
       block_number: felt,
       block_header_rlp_len: felt,
       block_header_rlp: felt*
    ):
    alloc_locals
    validate_provided_header_rlp(
        block_number,
        block_header_rlp_words_len,
        block_header_rlp_len,
        block_header_rlp)
    
    let (local state_root: Keccak256Hash) = decode_state_root(block_rlp=block_header_rlp, block_rlp_len=block_header_rlp_len)
    _block_state_root.write(block_number, state_root)
    return ()
end

@external
func set_block_transactions_root{
        pedersen_ptr: HashBuiltin*,
        syscall_ptr: felt*,
        bitwise_ptr : BitwiseBuiltin*,
        range_check_ptr
    } (block_header_rlp_words_len: felt,
       block_number: felt,
       block_header_rlp_len: felt,
       block_header_rlp: felt*
    ):
    alloc_locals
    validate_provided_header_rlp(
        block_number,
        block_header_rlp_words_len,
        block_header_rlp_len,
        block_header_rlp)
    
    let (local transactions_root: Keccak256Hash) = decode_transactions_root(block_rlp=block_header_rlp, block_rlp_len=block_header_rlp_len)
    _block_transactions_root.write(block_number, transactions_root)
    return ()
end

@external
func set_block_receipts_root{
        pedersen_ptr: HashBuiltin*,
        syscall_ptr: felt*,
        bitwise_ptr : BitwiseBuiltin*,
        range_check_ptr
    } (block_header_rlp_words_len: felt,
       block_number: felt,
       block_header_rlp_len: felt,
       block_header_rlp: felt*
    ):
    alloc_locals
    validate_provided_header_rlp(
        block_number,
        block_header_rlp_words_len,
        block_header_rlp_len,
        block_header_rlp)
    
    let (local receipts_root: Keccak256Hash) = decode_receipts_root(block_rlp=block_header_rlp, block_rlp_len=block_header_rlp_len)
    _block_receipts_root.write(block_number, receipts_root)
    return ()
end

@external
func set_block_uncles_hash{
        pedersen_ptr: HashBuiltin*,
        syscall_ptr: felt*,
        bitwise_ptr : BitwiseBuiltin*,
        range_check_ptr
    } (block_header_rlp_words_len: felt,
       block_number: felt,
       block_header_rlp_len: felt,
       block_header_rlp: felt*
    ):
    alloc_locals
    validate_provided_header_rlp(
        block_number,
        block_header_rlp_words_len,
        block_header_rlp_len,
        block_header_rlp)
    
    let (local uncles_hash: Keccak256Hash) = decode_uncles_hash(block_rlp=block_header_rlp, block_rlp_len=block_header_rlp_len)
    _block_uncles_hash.write(block_number, uncles_hash)
    return ()
end

@external
func set_block_difficulty{
        pedersen_ptr: HashBuiltin*,
        syscall_ptr: felt*,
        bitwise_ptr : BitwiseBuiltin*,
        range_check_ptr
    } (block_header_rlp_words_len: felt,
       block_number: felt,
       block_header_rlp_len: felt,
       block_header_rlp: felt*
    ):
    alloc_locals
    validate_provided_header_rlp(
        block_number,
        block_header_rlp_words_len,
        block_header_rlp_len,
        block_header_rlp)
    
    let (local difficulty: felt) = decode_difficulty(block_rlp=block_header_rlp, block_rlp_len=block_header_rlp_len)
    _block_difficulty.write(block_number, difficulty)
    return ()
end

@external
func set_block_beneficiary{
        pedersen_ptr: HashBuiltin*,
        syscall_ptr: felt*,
        bitwise_ptr : BitwiseBuiltin*,
        range_check_ptr
    } (block_header_rlp_words_len: felt,
       block_number: felt,
       block_header_rlp_len: felt,
       block_header_rlp: felt*
    ):
    alloc_locals
    validate_provided_header_rlp(
        block_number,
        block_header_rlp_words_len,
        block_header_rlp_len,
        block_header_rlp)
    
    let (local beneficiary: Address) = decode_beneficiary(block_rlp=block_header_rlp, block_rlp_len=block_header_rlp_len)
    _block_beneficiary.write(block_number, beneficiary)
    return ()
end

func validate_provided_header_rlp{
        pedersen_ptr: HashBuiltin*,
        syscall_ptr: felt*,
        bitwise_ptr : BitwiseBuiltin*,
        range_check_ptr
    } (block_number: felt,
       block_header_rlp_words_len: felt,
       block_header_rlp_len: felt,
       block_header_rlp: felt*
    ):
    alloc_locals
    local bitwise_ptr: BitwiseBuiltin* = bitwise_ptr
    let (local keccak_ptr : felt*) = alloc()
    let keccak_ptr_start = keccak_ptr

    let child_block_number = (block_number + 1)
    let (local child_block_parent: Keccak256Hash) = _block_parent_hash.read(block_number=child_block_number)

    let (provided_rlp_hash) = keccak256{keccak_ptr=keccak_ptr}(block_header_rlp, block_header_rlp_words_len)

    # Ensure child block parenthash matches provided rlp hash
    assert child_block_parent.word_1 = provided_rlp_hash[0]
    assert child_block_parent.word_2 = provided_rlp_hash[1]
    assert child_block_parent.word_3 = provided_rlp_hash[2]
    assert child_block_parent.word_4 = provided_rlp_hash[3]
    return ()
end
