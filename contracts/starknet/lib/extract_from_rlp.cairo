from starkware.cairo.common.cairo_builtins import BitwiseBuiltin
from starkware.cairo.common.math import unsigned_div_rem
from starkware.cairo.common.math_cmp import is_le
from starkware.cairo.common.alloc import alloc

from starknet.lib.bitshift import bitshift_right, bitshift_left
from starknet.lib.pow import pow

struct IntsSequence:
    member element : felt*
    member element_size: felt
end

struct RLPItem:
    member dataPosition : felt
    member length : felt
end


func getElement{ range_check_ptr }(rlp: felt*, rlp_len: felt, position: felt) -> (res: RLPItem):
    alloc_locals

    let (local data: IntsSequence) = extractData{ range_check_ptr = range_check_ptr }(position, 1, rlp, rlp_len)
    let firstByteArr: felt* = data.element
    let firstByte = firstByteArr[0]

    let (le_127) = is_le(firstByte, 127)

    if le_127 == 1:
        local result: RLPItem = RLPItem(position, 1)
        return (result)
    end

    let (le_183) = is_le(firstByte, 183)
    if le_183 == 1:
        local result: RLPItem = RLPItem(position+1, firstByte-128)
        return (result)
    end

    let (le_191) = is_le(firstByte, 191)
    if le_191 == 1:
        let lengthOfLength = firstByte - 183
        let (local bytes: IntsSequence) = extractData{ range_check_ptr = range_check_ptr }(position, 1, rlp, rlp_len)
        let lengthArr: felt* = bytes.element
        let length = lengthArr[0]

        local result: RLPItem = RLPItem(position + 1 + lengthOfLength, length)
        return (result)
    end

    let (le_247) = is_le(firstByte, 247)
    if le_247 == 1:
        local result: RLPItem = RLPItem(position+1, firstByte-192)
        return (result)
    end

    let lengthOfLength = firstByte - 247
    let (local bytes: IntsSequence) = extractData{ range_check_ptr = range_check_ptr }(position+1, lengthOfLength, rlp, rlp_len)
    let lengthArr: felt* = bytes.element
    let length = lengthArr[0]

    local result: RLPItem = RLPItem(position + 1 + lengthOfLength, length)
    return (result)
end

func extractElement{ range_check_ptr }(rlp: felt*, rlp_len: felt, position: felt) -> (res: IntsSequence):
    alloc_locals
    let (rlpItem: RLPItem) = getElement{ range_check_ptr = range_check_ptr }(rlp, rlp_len, position)

    if rlpItem.length == 0:
        let (local element: felt*) = alloc()
        local result: IntsSequence = IntsSequence(element, 0)
        tempvar range_check_ptr = range_check_ptr
        return (result)
    else: 
        tempvar range_check_ptr = range_check_ptr
    end

    return extractData{ range_check_ptr = range_check_ptr }(rlpItem.dataPosition, rlpItem.length, rlp, rlp_len)
end

func jumpOverElement{ range_check_ptr }(rlp: felt*, rlp_len: felt, position: felt) -> (res: felt):
    let (rlpItem: RLPItem) = getElement{ range_check_ptr = range_check_ptr }(rlp, rlp_len, position)
    return (rlpItem.dataPosition + rlpItem.length)
end

func extractData{ range_check_ptr }(start_pos: felt, size: felt, block_rlp: felt*, block_rlp_len: felt) -> (res: IntsSequence):
    alloc_locals

    let (start_word, left_shift) = unsigned_div_rem(start_pos, 8)
    let (end_word_tmp, end_pos_tmp) = unsigned_div_rem(start_pos + size, 8)

    local end_pos
    local end_word

    if end_pos_tmp == 0:
        end_pos = 8
        end_word = end_word_tmp - 1
    else:
        end_pos = end_pos_tmp
        end_word = end_word_tmp
    end


    local right_shift = 8 - left_shift

    let (full_words, remainder) = unsigned_div_rem(size, 8)

    let (local words_shifted : felt*) = alloc()

    if full_words != 0:
        shift_words{ range_check_ptr = range_check_ptr }(
            current_index=full_words - 1,
            start_word=start_word,
            left_shift=left_shift,
            right_shift=right_shift,
            block_rlp=block_rlp,
            block_rlp_len=block_rlp_len,
            accumulator=words_shifted,
            accumulator_len=full_words
        )
        tempvar range_check_ptr = range_check_ptr
    else:
        tempvar range_check_ptr = range_check_ptr
    end

    local range_check_ptr = range_check_ptr

    if remainder != 0:
        let (above_8) = is_le(9, remainder + left_shift)
        if above_8 == 1:
            let (left_part) = bitshift_left(block_rlp[end_word - 1], left_shift * 8)
            let (right_part) = bitshift_right(block_rlp[end_word], right_shift * 8)
            let final_word = left_part + right_part

            let (final_word_shifted) = bitshift_right(final_word, (8 - remainder) * 8)

            let (local divider: felt) = pow(2, remainder*8)
            let (_, new_word) = unsigned_div_rem(final_word_shifted, divider)

            assert words_shifted[full_words] = new_word

            tempvar range_check_ptr = range_check_ptr
        else:
            let (final_word_shifted) = bitshift_right(block_rlp[end_word], (8 - end_pos) * 8)

            let (local divider: felt) = pow(2, (end_pos-left_shift)*8)
            let (_, new_word) = unsigned_div_rem(final_word_shifted, divider)

            assert words_shifted[full_words] = new_word

            tempvar range_check_ptr = range_check_ptr
        end
        tempvar range_check_ptr = range_check_ptr
        let result: IntsSequence = IntsSequence(words_shifted, full_words+1)
        return (result)
    else:
        tempvar range_check_ptr = range_check_ptr
        let result: IntsSequence = IntsSequence(words_shifted, full_words)
        return (result)
    end
end

func shift_words{ range_check_ptr }(
    current_index: felt,
    start_word: felt,
    left_shift: felt,
    right_shift: felt,
    block_rlp: felt*,
    block_rlp_len: felt,
    accumulator: felt*,
    accumulator_len: felt):
    alloc_locals

    if current_index == -1:
        tempvar range_check_ptr = range_check_ptr
        return ()
    else:
        if left_shift != 0:
            let (left_part) = bitshift_left(block_rlp[start_word + current_index], left_shift * 8)
            let (right_part) = bitshift_right(block_rlp[start_word + current_index + 1], right_shift * 8)
        
            local new_word = left_part + right_part
            let (local divider: felt) = pow(2, 64)
            let (_, new_word_masked) = unsigned_div_rem(new_word, divider)

            assert accumulator[current_index] = new_word_masked
            tempvar range_check_ptr = range_check_ptr
        else:
            assert accumulator[current_index] = block_rlp[start_word + current_index]
            tempvar range_check_ptr = range_check_ptr
        end

        shift_words{ range_check_ptr = range_check_ptr }(
            current_index=current_index - 1,
            start_word=start_word,
            left_shift=left_shift,
            right_shift=right_shift,
            block_rlp=block_rlp,
            block_rlp_len=block_rlp_len,
            accumulator=accumulator,
            accumulator_len=accumulator_len)

        tempvar range_check_ptr = range_check_ptr
    end
    return ()
end

func is_rlp_list{ range_check_ptr }(pos: felt, rlp: felt*, rlp_len: felt) -> (res: felt):
    alloc_locals
    let (local data: IntsSequence) = extractData(pos, 1, rlp, rlp_len)
    let (is_list) = is_le(191, data.element[0])
    return (is_list)
end

func to_list{ range_check_ptr }(rlp: felt*, rlp_len: felt) -> (items: RLPItem*, items_len: felt):
    alloc_locals

    let (is_list) = is_rlp_list(0, rlp, rlp_len)
    assert is_list = 1

    let (local payload: RLPItem) = getElement(rlp, rlp_len, 0)

    local payload_pos = payload.dataPosition
    local payload_len = payload.length

    let payload_end = payload_pos + payload_len
    let next_element_pos = payload_pos

    let (local items : RLPItem*) = alloc()
    let (items_len) = to_list_recursive(rlp, rlp_len, next_element_pos, payload_end, 0, items, 0)
    return (items, items_len)
end

func to_list_recursive{ range_check_ptr }(
    rlp: felt*,
    rlp_len: felt,
    next_element_pos: felt,
    payload_end: felt,
    current_index: felt,
    accumulator: RLPItem*,
    accumulator_len: felt) -> (res: felt):
    alloc_locals

    let (break) = is_le(payload_end, next_element_pos)
    if break == 1:
        return (current_index)
    end

    let (local payload: RLPItem) = getElement(rlp, rlp_len, next_element_pos)

    local payload_pos = payload.dataPosition
    local payload_len = payload.length

    assert accumulator[current_index] = RLPItem(payload_pos, payload_len)
    return to_list_recursive(
        rlp=rlp,
        rlp_len=rlp_len,
        next_element_pos=payload_pos + payload_len,
        payload_end=payload_end,
        current_index=current_index+1,
        accumulator=accumulator,
        accumulator_len=accumulator_len+1
        )
end

func extract_list_values{ range_check_ptr }(rlp: felt*, rlp_len: felt, rlp_items: RLPItem*, rlp_items_len: felt) -> (res: felt*, res_len: felt):
    alloc_locals
    let (local acc: IntsSequence*) = alloc()
    extract_list_values_recursive(rlp, rlp_len, rlp_items, rlp_items_len, acc, 0, 0)
    return (acc, rlp_items_len)
end

func extract_list_values_recursive{ range_check_ptr }(
    rlp: felt*,
    rlp_len: felt,
    rlp_items: RLPItem*,
    rlp_items_len: felt,
    acc: IntsSequence*,
    acc_len: felt,
    current_index: felt):
    alloc_locals
    if current_index == rlp_items_len:
        return ()
    end

    let (local data: IntsSequence) = extractData(rlp_items[current_index].dataPosition, rlp_items[current_index].length, rlp, rlp_len)
    assert acc[current_index] = data

    return extract_list_values_recursive(
        rlp=rlp,
        rlp_len=rlp_len,
        rlp_items=rlp_items,
        rlp_items_len=rlp_items_len,
        acc=acc,
        acc_len=acc_len,
        current_index=current_index + 1)
end
