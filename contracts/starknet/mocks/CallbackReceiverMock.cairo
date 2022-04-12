%lang starknet
%builtins pedersen range_check ecdsa

from starkware.cairo.common.cairo_builtins import HashBuiltin

@storage_var
func _twap() -> (res: felt):
end

@view
func twap{
        syscall_ptr: felt*,
        pedersen_ptr: HashBuiltin*,
        range_check_ptr
    } () -> (res: felt):
    return _twap.read()
end

@external 
func twap_callback{
        pedersen_ptr: HashBuiltin*,
        syscall_ptr: felt*,
        range_check_ptr
    } (computation_id: felt, twap: felt):
    _twap.write(twap)
    return ()
end