from starkware.cairo.common.math import assert_le
from starknet.lib.extract_from_rlp import extract_data, extractElement, jumpOverElement, to_list
from starknet.types import (Keccak256Hash, Address, IntsSequence)

### Elements decoder 
const PARENT_HASH = 0
const OMMERS_HASH = 1
const BENEFICIARY = 2
const STATE_ROOT = 3
const TRANSACTION_ROOT = 4
const RECEIPTS_ROOT = 5
const LOGS_BLOOM = 6
const DIFFICULTY = 7
const BLOCK_NUMBER = 8
const GAS_LIMIT = 9
const GAS_USED = 10
const TIMESTAMP = 11
const EXTRA_DATA = 12
const MIX_HASH = 13
const NONCE = 14
const BASE_FEE = 15

func decode_parent_hash{ range_check_ptr }(block_rlp: IntsSequence) -> (res: Keccak256Hash):
    alloc_locals
    let (local data: IntsSequence) = extract_data(4, 32, block_rlp)
    let parent_hash = data.element
    local hash: Keccak256Hash = Keccak256Hash(
        word_1=parent_hash[0],
        word_2=parent_hash[1],
        word_3=parent_hash[2],
        word_4=parent_hash[3]
    )
    return (hash)
end

func decode_uncles_hash{ range_check_ptr }(block_rlp: IntsSequence) -> (res: Keccak256Hash):
    alloc_locals
    let (local data: IntsSequence) = extract_data(4+32+1, 32, block_rlp)
    let uncles_hash = data.element
    local hash: Keccak256Hash = Keccak256Hash(
        word_1=uncles_hash[0],
        word_2=uncles_hash[1],
        word_3=uncles_hash[2],
        word_4=uncles_hash[3]
    )
    return (hash)
end

func decode_beneficiary{ range_check_ptr }(block_rlp: IntsSequence) -> (res: Address):
    alloc_locals
    let (local data: IntsSequence) = extract_data(4+32+1+32+1, 20, block_rlp)
    let beneficiary = data.element
    local address: Address = Address(
        word_1=beneficiary[0],
        word_2=beneficiary[1],
        word_3=beneficiary[2]
    )
    return (address)
end

func decode_state_root{ range_check_ptr }(block_rlp: IntsSequence) -> (res: Keccak256Hash):
    alloc_locals
    let (local data: IntsSequence) = extract_data(4+32+1+32+1+20+1, 32, block_rlp)
    let state_root = data.element
    local hash: Keccak256Hash = Keccak256Hash(
        word_1=state_root[0],
        word_2=state_root[1],
        word_3=state_root[2],
        word_4=state_root[3]
    )
    return (hash)
end

func decode_transactions_root{ range_check_ptr }(block_rlp: IntsSequence) -> (res: Keccak256Hash):
    alloc_locals
    let (local data: IntsSequence) = extract_data(4+32+1+32+1+20+1+32+1, 32, block_rlp)
    let transactions_root = data.element
    local hash: Keccak256Hash = Keccak256Hash(
        word_1=transactions_root[0],
        word_2=transactions_root[1],
        word_3=transactions_root[2],
        word_4=transactions_root[3]
    )
    return (hash)
end

func decode_receipts_root{ range_check_ptr }(block_rlp: IntsSequence) -> (res: Keccak256Hash):
    alloc_locals
    let (local data: IntsSequence) = extract_data(4+32+1+32+1+20+1+32+1+32+1, 32, block_rlp)
    let receipts_root = data.element
    local hash: Keccak256Hash = Keccak256Hash(
        word_1=receipts_root[0],
        word_2=receipts_root[1],
        word_3=receipts_root[2],
        word_4=receipts_root[3]
    )
    return (hash)
end

func decode_difficulty{ range_check_ptr }(block_rlp: IntsSequence) -> (res: felt):
    alloc_locals
    let (rlp_items, rlp_items_len) = to_list(block_rlp)
    assert_le(DIFFICULTY + 1, rlp_items_len)
    let (local difficulty_rlp_element: IntsSequence) = extract_data(rlp_items[DIFFICULTY].dataPosition, rlp_items[DIFFICULTY].length, block_rlp)
    local difficulty = difficulty_rlp_element.element[0]
    return (difficulty)
end

func decode_block_number{ range_check_ptr }(block_rlp: IntsSequence) -> (res: felt):
    alloc_locals
    let (rlp_items, rlp_items_len) = to_list(block_rlp)
    assert_le(BLOCK_NUMBER + 1, rlp_items_len)
    let (local block_number_rlp_element: IntsSequence) = extract_data(rlp_items[BLOCK_NUMBER].dataPosition, rlp_items[BLOCK_NUMBER].length, block_rlp)
    local block_number = block_number_rlp_element.element[0]
    return (block_number)
end

func decode_gas_limit{ range_check_ptr }(block_rlp: IntsSequence) -> (res: felt):
    alloc_locals
    let (rlp_items, rlp_items_len) = to_list(block_rlp)
    assert_le(GAS_LIMIT + 1, rlp_items_len)
    let (local gas_limit_rlp_element: IntsSequence) = extract_data(rlp_items[GAS_LIMIT].dataPosition, rlp_items[GAS_LIMIT].length, block_rlp)
    local gas_limit = gas_limit_rlp_element.element[0]
    return (gas_limit)
end

func decode_gas_used{ range_check_ptr }(block_rlp: IntsSequence) -> (res: felt):
    alloc_locals
    let (rlp_items, rlp_items_len) = to_list(block_rlp)
    assert_le(GAS_USED + 1, rlp_items_len)
    let (local gas_used_rlp_element: IntsSequence) = extract_data(rlp_items[GAS_USED].dataPosition, rlp_items[GAS_USED].length, block_rlp)
    local gas_used = gas_used_rlp_element.element[0]
    return (gas_used)
end

func decode_timestamp{ range_check_ptr }(block_rlp: IntsSequence) -> (res: felt):
    alloc_locals
    let (rlp_items, rlp_items_len) = to_list(block_rlp)
    assert_le(TIMESTAMP + 1, rlp_items_len)
    let (local timestamp_rlp_element: IntsSequence) = extract_data(rlp_items[TIMESTAMP].dataPosition, rlp_items[TIMESTAMP].length, block_rlp)
    local timestamp = timestamp_rlp_element.element[0]
    return (timestamp)
end

func decode_base_fee{ range_check_ptr }(block_rlp: IntsSequence) -> (res: felt):
    alloc_locals
    let (rlp_items, rlp_items_len) = to_list(block_rlp)
    assert_le(BASE_FEE + 1, rlp_items_len)
    let (local base_fee_rlp_element: IntsSequence) = extract_data(rlp_items[BASE_FEE].dataPosition, rlp_items[BASE_FEE].length, block_rlp)
    local base_fee = base_fee_rlp_element.element[0]
    return (base_fee)
end