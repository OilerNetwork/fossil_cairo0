from starkware.cairo.common.cairo_builtins import BitwiseBuiltin

struct Keccak256Hash:
    member word_1 : felt
    member word_2 : felt
    member word_3 : felt
    member word_4 : felt
end

func decode_parent_hash(block_rlp: felt*, block_rlp_len: felt) -> (res: Keccak256Hash):
    alloc_locals
    local hash: Keccak256Hash = Keccak256Hash(
        word_1=block_rlp[1],
        word_2=block_rlp[2],
        word_3=block_rlp[3],
        word_4=block_rlp[4]
    ) 

    return (hash)
end
