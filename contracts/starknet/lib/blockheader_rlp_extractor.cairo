from starknet.lib.extract_from_rlp import extractData, extractElement, jumpOverElement
from starknet.types import (Keccak256Hash, Address, IntsSequence)

### Elements decoder 

func decode_parent_hash{ range_check_ptr }(block_rlp: felt*, block_rlp_len: felt) -> (res: Keccak256Hash):
    alloc_locals
    let (local data: IntsSequence) = extractData(4, 32, block_rlp, block_rlp_len)
    let parent_hash = data.element
    local hash: Keccak256Hash = Keccak256Hash(
        word_1=parent_hash[0],
        word_2=parent_hash[1],
        word_3=parent_hash[2],
        word_4=parent_hash[3]
    )
    return (hash)
end

func decode_uncles_hash{ range_check_ptr }(block_rlp: felt*, block_rlp_len: felt) -> (res: Keccak256Hash):
    alloc_locals
    let (local data: IntsSequence) = extractData(4+32+1, 32, block_rlp, block_rlp_len)
    let uncles_hash = data.element
    local hash: Keccak256Hash = Keccak256Hash(
        word_1=uncles_hash[0],
        word_2=uncles_hash[1],
        word_3=uncles_hash[2],
        word_4=uncles_hash[3]
    )
    return (hash)
end

func decode_beneficiary{ range_check_ptr }(block_rlp: felt*, block_rlp_len: felt) -> (res: Address):
    alloc_locals
    let (local data: IntsSequence) = extractData(4+32+1+32+1, 20, block_rlp, block_rlp_len)
    let beneficiary = data.element
    local address: Address = Address(
        word_1=beneficiary[0],
        word_2=beneficiary[1],
        word_3=beneficiary[2]
    )
    return (address)
end

func decode_state_root{ range_check_ptr }(block_rlp: felt*, block_rlp_len: felt) -> (res: Keccak256Hash):
    alloc_locals
    let (local data: IntsSequence) = extractData(4+32+1+32+1+20+1, 32, block_rlp, block_rlp_len)
    let state_root = data.element
    local hash: Keccak256Hash = Keccak256Hash(
        word_1=state_root[0],
        word_2=state_root[1],
        word_3=state_root[2],
        word_4=state_root[3]
    )
    return (hash)
end

func decode_transactions_root{ range_check_ptr }(block_rlp: felt*, block_rlp_len: felt) -> (res: Keccak256Hash):
    alloc_locals
    let (local data: IntsSequence) = extractData(4+32+1+32+1+20+1+32+1, 32, block_rlp, block_rlp_len)
    let transactions_root = data.element
    local hash: Keccak256Hash = Keccak256Hash(
        word_1=transactions_root[0],
        word_2=transactions_root[1],
        word_3=transactions_root[2],
        word_4=transactions_root[3]
    )
    return (hash)
end

func decode_receipts_root{ range_check_ptr }(block_rlp: felt*, block_rlp_len: felt) -> (res: Keccak256Hash):
    alloc_locals
    let (local data: IntsSequence) = extractData(4+32+1+32+1+20+1+32+1+32+1, 32, block_rlp, block_rlp_len)
    let receipts_root = data.element
    local hash: Keccak256Hash = Keccak256Hash(
        word_1=receipts_root[0],
        word_2=receipts_root[1],
        word_3=receipts_root[2],
        word_4=receipts_root[3]
    )
    return (hash)
end

func decode_difficulty{ range_check_ptr }(block_rlp: felt*, block_rlp_len: felt) -> (res: felt):
    alloc_locals
    let (local difficulty_rlp_element: IntsSequence) = extractElement(block_rlp, block_rlp_len, 448)
    local difficulty = difficulty_rlp_element.element[0]
    return (difficulty)
end

func decode_block_number{ range_check_ptr }(block_rlp: felt*, block_rlp_len: felt) -> (res: felt):
    alloc_locals
    let (blockNumberPosition) = jumpOverElement(block_rlp, block_rlp_len, 448)
    let (local block_number_rlp_element: IntsSequence) = extractElement(block_rlp, block_rlp_len, blockNumberPosition)
    local block_number = block_number_rlp_element.element[0]
    return (block_number)
end