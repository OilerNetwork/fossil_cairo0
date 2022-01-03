func arr_eq(a: felt*, a_len: felt, b: felt*, b_len: felt) -> (res: felt):
    if a_len != b_len:
        return (0)
    end
    if a_len == 0:
        return (1)
    end
    return _arr_eq(a=a, a_len=a_len, b=b, b_len=b_len, current_index=a_len-1)
end

func _arr_eq(a: felt*, a_len: felt, b: felt*, b_len: felt, current_index: felt) -> (res: felt):
    if current_index == -1:
        return (1)
    end

    if a[current_index] != b[current_index]:
        return (0)
    end
    return _arr_eq(a=a, a_len=a_len, b=b, b_len=b_len, current_index=current_index-1)
end