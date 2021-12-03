from starknet.lib.extract_from_rlp import extractData, extractElement, jumpOverElement

struct Keccak256Hash:
    member word_1 : felt
    member word_2 : felt
    member word_3 : felt
    member word_4 : felt
end

### Elements decoder 

func decode_parent_hash{ range_check_ptr }(block_rlp: felt*, block_rlp_len: felt) -> (res: Keccak256Hash):
    alloc_locals
    let (_, parent_hash) = extractData(4, 32, block_rlp, block_rlp_len)
    local hash: Keccak256Hash = Keccak256Hash(
        word_1=parent_hash[0],
        word_2=parent_hash[1],
        word_3=parent_hash[2],
        word_4=parent_hash[3]
    )
    return (hash)
end
