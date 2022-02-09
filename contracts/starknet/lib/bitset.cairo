from starknet.lib.pow import pow
from starkware.cairo.common.math import unsigned_div_rem

# Argument bitset: n bits number in range(0, 2**n - 1)
# Argument position: counted from the right, from zero
# Returns a number in range(0, 1) if the bit is set to 1 or to 0
func bitset_get{ range_check_ptr }(bitset: felt, position: felt) -> (res: felt):
    let (divider) = pow(2, position)
    # shift right (divide)
    let (q, _) = unsigned_div_rem(bitset, divider)
    # exctract bit with mod 2
    let (_, r) = unsigned_div_rem(q, 2)
    return (r)
end