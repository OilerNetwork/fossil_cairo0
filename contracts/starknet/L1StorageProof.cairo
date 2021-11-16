%lang starknet
%builtins pedersen range_check ecdsa bitwise

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.cairo_builtins import BitwiseBuiltin
from starkware.starknet.common.syscalls import get_caller_address
from starkware.cairo.common.alloc import alloc

from starknet.lib.keccak import keccak256

struct Keccak256Hash:
    member word_1 : felt
    member word_2 : felt
    member word_3 : felt
    member word_4 : felt
end


@storage_var
func _l1_blockhash() -> (res: Keccak256Hash):
end

@storage_var
func _l1_messages_origin() -> (res: felt):
end

### Processed blocks info ###

@storage_var
func _processed_block_hash(block_number: felt) -> (res: Keccak256Hash):
end

@storage_var
func _processed_block_parent_hash(block_number: felt) -> (res: Keccak256Hash):
end

@storage_var
func _processed_block_state_root(block_number: felt) -> (res: Keccak256Hash):
end

@storage_var
func _processed_block_receipts_root(block_number: felt) -> (res: Keccak256Hash):
end

# Helper var - mutated every time a block is processed
@storage_var
func _oldest_processed_block() -> (res: felt):
end

# Helper var - set only once when the l1 originated blockhash is processed
@storage_var
func _youngest_processed_block() -> (res: felt):
end

#############################

@storage_var
func _initialized() -> (res: felt):
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
func submit_l1_blockhash{
        pedersen_ptr: HashBuiltin*,
        syscall_ptr: felt*,
        range_check_ptr
    } (blockhash: Keccak256Hash):
    let (caller) = get_caller_address()
    let (l1_messages_origin) = _l1_messages_origin.read()
    assert caller = l1_messages_origin
    _l1_blockhash.write(blockhash)
    return ()
end

@external
func process_block{
        pedersen_ptr: HashBuiltin*,
        syscall_ptr: felt*,
        bitwise_ptr : BitwiseBuiltin*,
        range_check_ptr,
    } (block_header_rlp_len: felt, block_header_rlp: felt*):
    alloc_locals
    local bitwise_ptr_start : BitwiseBuiltin* = bitwise_ptr
    let (local keccak_ptr : felt*) = alloc()
    let keccak_ptr_start = keccak_ptr

    let (submitted_block_hash) = keccak256{keccak_ptr=keccak_ptr}(block_header_rlp, block_header_rlp_len)
    let (oldest_processed_block) = _oldest_processed_block.read()

    # Storage slot not initialized
    if oldest_processed_block == 0:
        let (l1_originated_block_hash: Keccak256Hash) = _l1_blockhash.read()

        local pedersen_ptr : HashBuiltin* = pedersen_ptr
        local range_check_ptr = range_check_ptr
        local bitwise_ptr: BitwiseBuiltin* = bitwise_ptr
        local keccak_ptr: felt* = keccak_ptr
        local syscall_ptr: felt* = syscall_ptr

        local l1_originated_block_hash_cp: Keccak256Hash = l1_originated_block_hash

        assert submitted_block_hash[0] = l1_originated_block_hash.word_1
        assert submitted_block_hash[1] = l1_originated_block_hash.word_2
        assert submitted_block_hash[2] = l1_originated_block_hash.word_3
        assert submitted_block_hash[3] = l1_originated_block_hash.word_4
        
        let (block_number, parent_hash, state_root, receipts_root) = extract_from_rlp(block_header_rlp)
        
        _processed_block_hash.write(block_number, l1_originated_block_hash_cp)
        _processed_block_parent_hash.write(block_number, parent_hash)
        _processed_block_state_root.write(block_number, state_root)
        _processed_block_receipts_root.write(block_number, receipts_root)

        _oldest_processed_block.write(block_number)
        _youngest_processed_block.write(block_number)
        return ()
    end

    let (oldest_block) = _oldest_processed_block.read()
    let (oldest_block_parent_hash) = _processed_block_parent_hash.read(oldest_block)

    local pedersen_ptr : HashBuiltin* = pedersen_ptr
    local range_check_ptr = range_check_ptr
    local bitwise_ptr: BitwiseBuiltin* = bitwise_ptr
    local keccak_ptr: felt* = keccak_ptr
    local syscall_ptr: felt* = syscall_ptr

    local oldest_block_parent_hash_cp: Keccak256Hash = oldest_block_parent_hash

    assert submitted_block_hash[0] = oldest_block_parent_hash.word_1
    assert submitted_block_hash[1] = oldest_block_parent_hash.word_2
    assert submitted_block_hash[2] = oldest_block_parent_hash.word_3
    assert submitted_block_hash[3] = oldest_block_parent_hash.word_4

    let (block_number, parent_hash, state_root, receipts_root) = extract_from_rlp(block_header_rlp)

    _processed_block_hash.write(block_number, oldest_block_parent_hash_cp)
    _processed_block_parent_hash.write(block_number, parent_hash)
    _processed_block_state_root.write(block_number, state_root)
    _processed_block_receipts_root.write(block_number, receipts_root)

    _oldest_processed_block.write(block_number)
    return ()
end

func extract_from_rlp(block_header_rlp: felt*) -> (block_number: felt, parent_hash: Keccak256Hash, state_root: Keccak256Hash, receipts_root: Keccak256Hash):
    return (
    block_number=block_header_rlp[8],
    parent_hash=Keccak256Hash(
        word_1=block_header_rlp[0],
        word_2=block_header_rlp[1],
        word_3=block_header_rlp[2],
        word_4=block_header_rlp[3]
    ),
    state_root=Keccak256Hash(
        word_1=block_header_rlp[3],
        word_2=block_header_rlp[4],
        word_3=block_header_rlp[5],
        word_4=block_header_rlp[6],
    ),
    receipts_root=Keccak256Hash(
        word_1=block_header_rlp[5],
        word_2=block_header_rlp[6],
        word_3=block_header_rlp[7],
        word_4=block_header_rlp[8],
    ))
end

