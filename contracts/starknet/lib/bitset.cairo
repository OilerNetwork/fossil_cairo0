from starknet.lib.pow import pow
from starkware.cairo.common.math import unsigned_div_rem

# Argument bitset: 4bit number in range(0, 15)
# Argument position: counted from the left
# Returns a number in range(0, 1)
func bitset4_get{ range_check_ptr }(bitset: felt, position: felt) -> (res: felt):
    let (divider) = pow(2, 4 - position)
    let (q1, r1) = unsigned_div_rem(bitset, divider)
    let (q, r) = unsigned_div_rem(q1, 2)
    return (r)
end

# Argument bitset: 6bit number in range(0, 63)
# Argument position: counted from the left
# Returns a number in range(0, 1)
func bitset6_get{ range_check_ptr }(bitset: felt, position: felt) -> (res: felt):
    let (divider) = pow(2, 6 - position)
    let (q1, r1) = unsigned_div_rem(bitset, divider)
    let (q, r) = unsigned_div_rem(q1, 2)
    return (r)
end