from starkware.cairo.common.cairo_builtins import BitwiseBuiltin

func to_big_endian{ bitwise_ptr : BitwiseBuiltin* }(word: felt) -> (res: felt):
    return (word)
end