from starkware.cairo.common.cairo_builtins import BitwiseBuiltin
from starkware.cairo.common.math import unsigned_div_rem
from starkware.cairo.common.math_cmp import is_le
from starkware.cairo.common.alloc import alloc

from starknet.types import IntsSequence, RLPItem
from starknet.lib.bitshift import bitshift_right, bitshift_left
from starknet.lib.pow import pow


func getElement{ range_check_ptr }(rlp: IntsSequence, position: felt) -> (res: RLPItem):
    alloc_locals

    let (local data: IntsSequence) = extract_data{ range_check_ptr = range_check_ptr }(position, 1, rlp)
    let firstByteArr: felt* = data.element
    let firstByte = firstByteArr[0]

    let (le_127) = is_le(firstByte, 127)

    if le_127 == 1:
        local result: RLPItem = RLPItem(firstByte, position, 1)
        return (result)
    end

    let (le_183) = is_le(firstByte, 183)
    if le_183 == 1:
        local result: RLPItem = RLPItem(firstByte, position+1, firstByte-128)
        return (result)
    end

    let (le_191) = is_le(firstByte, 191)
    if le_191 == 1:
        let lengthOfLength = firstByte - 183
        let (local bytes: IntsSequence) = extract_data{ range_check_ptr = range_check_ptr }(position + 1, lengthOfLength, rlp)
        let lengthArr: felt* = bytes.element
        let length = lengthArr[0]

        local result: RLPItem = RLPItem(firstByte, position + 1 + lengthOfLength, length)
        return (result)
    end

    let (le_247) = is_le(firstByte, 247)
    if le_247 == 1:
        local result: RLPItem = RLPItem(firstByte, position+1, firstByte-192)
        return (result)
    end

    let lengthOfLength = firstByte - 247
    let (local bytes: IntsSequence) = extract_data{ range_check_ptr = range_check_ptr }(position+1, lengthOfLength, rlp)
    let lengthArr: felt* = bytes.element
    let length = lengthArr[0]

    local result: RLPItem = RLPItem(firstByte, position + 1 + lengthOfLength, length)
    return (result)
end

func extractElement{ range_check_ptr }(rlp: IntsSequence, position: felt) -> (res: IntsSequence):
    alloc_locals
    let (rlpItem: RLPItem) = getElement{ range_check_ptr = range_check_ptr }(rlp, position)

    if rlpItem.length == 0:
        let (local element: felt*) = alloc()
        local result: IntsSequence = IntsSequence(element, 0, 0)
        tempvar range_check_ptr = range_check_ptr
        return (result)
    else: 
        tempvar range_check_ptr = range_check_ptr
    end

    return extract_data{ range_check_ptr = range_check_ptr }(rlpItem.dataPosition, rlpItem.length, rlp)
end

func jumpOverElement{ range_check_ptr }(rlp: IntsSequence, position: felt) -> (res: felt):
    let (rlpItem: RLPItem) = getElement{ range_check_ptr = range_check_ptr }(rlp, position)
    return (rlpItem.dataPosition + rlpItem.length)
end

func extract_data{ range_check_ptr }(start_pos: felt, size: felt, rlp: IntsSequence) -> (res: IntsSequence):
    alloc_locals
    let (start_word, left_shift) = unsigned_div_rem(start_pos, 8)
    let (end_word_tmp, end_pos_tmp) = unsigned_div_rem(start_pos + size, 8)

    let (full_words, remainder) = unsigned_div_rem(size, 8)

    # end_pos is a bad name - it conflicts with start_pos
    # start_pos is absolute, and end_pos is relative inside the world
    local end_pos
    local end_word
    if end_pos_tmp == 0:
        end_pos = 8
        end_word = end_word_tmp - 1
    else:
        end_pos = end_pos_tmp
        end_word = end_word_tmp
    end

    let (_, last_rlp_word_len_tmp) = unsigned_div_rem(rlp.element_size_bytes, 8)
    local last_rlp_word_len
    if last_rlp_word_len_tmp == 0:
        last_rlp_word_len = 8
    else:
        last_rlp_word_len = last_rlp_word_len_tmp
    end

    local right_shift = 8 - left_shift
    let last_word_right_shift = last_rlp_word_len - left_shift

    let (local new_words : felt*) = alloc()

    let (local new_words_len) = extract_data_rec(
        start_word=start_word,
        full_words=full_words,
        left_shift=left_shift,
        right_shift=right_shift,
        last_word_right_shift=last_word_right_shift,
        rlp=rlp,
        acc=new_words,
        acc_len=0,
        current_index=start_word)

    local result_words_len
    
    if remainder == 0:
        result_words_len = new_words_len
        tempvar range_check_ptr = range_check_ptr
    else:
        let (local left_shift_above_8_bytes) = is_le(8 + 1, remainder + left_shift)
        if left_shift_above_8_bytes == 1:
            let (local left_part) = bitshift_left(rlp.element[end_word - 1], left_shift * 8)

            local right_part
            if end_word == rlp.element_size_words - 1:
                let (local is_last_word_right_shift_negative) = is_le(last_word_right_shift + 8, 7)
                if is_last_word_right_shift_negative == 1:
                    let (local right_part_tmp) = bitshift_left(rlp.element[end_word], -8 * last_word_right_shift)
                    right_part = right_part_tmp
                    tempvar range_check_ptr = range_check_ptr
                else:
                    let (local right_part_tmp) = bitshift_right(rlp.element[end_word], 8 * last_word_right_shift)
                    right_part = right_part_tmp
                    tempvar range_check_ptr = range_check_ptr
                end
            else:
                let (local right_part_tmp) = bitshift_right(rlp.element[end_word], 8 * right_shift)
                right_part = right_part_tmp
                tempvar range_check_ptr = range_check_ptr
            end

            local final_word = left_part + right_part
            let (local final_word_shifted) = bitshift_right(final_word, 8 * (8 - remainder))

            let (local divider: felt) = pow(2, remainder * 8)
            let (_, final_word_masked) = unsigned_div_rem(final_word_shifted, divider)
            assert new_words[new_words_len] = final_word_masked
        else:
            local final_word_shifted
            if end_word == rlp.element_size_words - 1:
                let (local final_word_shifted_tmp) = bitshift_right(rlp.element[end_word], 8 * (last_rlp_word_len - end_pos))
                final_word_shifted = final_word_shifted_tmp
                tempvar range_check_ptr = range_check_ptr
            else:
                let (local final_word_shifted_tmp) = bitshift_right(rlp.element[end_word], 8 * (8 - end_pos))
                final_word_shifted = final_word_shifted_tmp
                tempvar range_check_ptr = range_check_ptr
            end

            let (local divider: felt) = pow(2, 8 * (end_pos - left_shift))
            let (_, final_word_masked) = unsigned_div_rem(final_word_shifted, divider)
            assert new_words[new_words_len] = final_word_masked
        end
        result_words_len = new_words_len + 1
        tempvar range_check_ptr = range_check_ptr
    end

    local result: IntsSequence = IntsSequence(new_words, result_words_len, size)
    return (result)
end

func extract_data_rec{ range_check_ptr }(
    start_word: felt,
    full_words: felt,
    left_shift: felt,
    right_shift: felt,
    last_word_right_shift: felt,
    rlp: IntsSequence,
    acc: felt*,
    acc_len: felt,
    current_index: felt) -> (new_acc_size: felt):
    alloc_locals

    if current_index == full_words + start_word:
        return (acc_len)
    end

    let (local left_part) = bitshift_left(rlp.element[current_index], left_shift * 8)
    local right_part
    if current_index == rlp.element_size_words - 2:
        let (local is_last_word_right_shift_negative) = is_le(last_word_right_shift, -1)
        if is_last_word_right_shift_negative == 1:
            let (local right_part_tmp) = bitshift_left(rlp.element[current_index + 1], -8 * last_word_right_shift)
            right_part = right_part_tmp
            tempvar range_check_ptr = range_check_ptr
        else:
            let (local right_part_tmp) = bitshift_right(rlp.element[current_index + 1], 8 * last_word_right_shift)
            right_part = right_part_tmp
            tempvar range_check_ptr = range_check_ptr
        end
        tempvar range_check_ptr = range_check_ptr
    else:
        if current_index == rlp.element_size_words - 1:
            right_part = 0
            tempvar range_check_ptr = range_check_ptr
        else:
            let (local right_part_tmp) = bitshift_right(rlp.element[current_index + 1], 8 * right_shift)
            right_part = right_part_tmp
            tempvar range_check_ptr = range_check_ptr
        end
        tempvar range_check_ptr = range_check_ptr
    end

    local new_word = left_part + right_part
    let (local divider: felt) = pow(2, 64)

    local range_check_ptr = range_check_ptr

    let (_, new_word_masked) = unsigned_div_rem(new_word, divider)

    local range_check_ptr = range_check_ptr

    assert acc[current_index - start_word] = new_word_masked

    return extract_data_rec(
        start_word=start_word,
        full_words=full_words,
        left_shift=left_shift,
        right_shift=right_shift,
        last_word_right_shift=last_word_right_shift,
        rlp=rlp,
        acc=acc,
        acc_len=acc_len + 1,
        current_index=current_index + 1)
end

func is_rlp_list{ range_check_ptr }(pos: felt, rlp: IntsSequence) -> (res: felt):
    alloc_locals
    let (local data: IntsSequence) = extract_data(pos, 1, rlp)
    let (is_list) = is_le(191, data.element[0])
    return (is_list)
end

func is_rlp_list_rlp_item{ range_check_ptr }(item: RLPItem, rlp: IntsSequence) -> (res: felt):
    alloc_locals
    local firstByte = item.firstByte
    let (is_list) = is_le(191, firstByte)
    return (is_list)
end

func to_list{ range_check_ptr }(rlp: IntsSequence) -> (items: RLPItem*, items_len: felt):
    alloc_locals

    let (is_list) = is_rlp_list(0, rlp)
    assert is_list = 1

    let (local payload: RLPItem) = getElement(rlp, 0)

    local payload_pos = payload.dataPosition
    local payload_len = payload.length

    let payload_end = payload_pos + payload_len
    let next_element_pos = payload_pos

    let (local items : RLPItem*) = alloc()
    let (items_len) = to_list_recursive(rlp, next_element_pos, payload_end, 0, items, 0)
    return (items, items_len)
end

func to_list_recursive{ range_check_ptr }(
    rlp: IntsSequence,
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

    let (local payload: RLPItem) = getElement(rlp, next_element_pos)

    local payload_firstByte = payload.firstByte
    local payload_pos = payload.dataPosition
    local payload_len = payload.length

    assert accumulator[current_index] = RLPItem(payload_firstByte, payload_pos, payload_len)
    return to_list_recursive(
        rlp=rlp,
        next_element_pos=payload_pos + payload_len,
        payload_end=payload_end,
        current_index=current_index+1,
        accumulator=accumulator,
        accumulator_len=accumulator_len+1
        )
end

func extract_list_values{ range_check_ptr }(rlp: IntsSequence, rlp_items: RLPItem*, rlp_items_len: felt) -> (res: IntsSequence*, res_len: felt):
    alloc_locals
    let (local acc: IntsSequence*) = alloc()
    extract_list_values_recursive(rlp, rlp_items, rlp_items_len, acc, 0, 0)
    return (acc, rlp_items_len)
end

func extract_list_values_recursive{ range_check_ptr }(
    rlp: IntsSequence,
    rlp_items: RLPItem*,
    rlp_items_len: felt,
    acc: IntsSequence*,
    acc_len: felt,
    current_index: felt):
    alloc_locals
    if current_index == rlp_items_len:
        return ()
    end

    let (local data: IntsSequence) = extract_data(rlp_items[current_index].dataPosition, rlp_items[current_index].length, rlp)
    assert acc[current_index] = data

    return extract_list_values_recursive(
        rlp=rlp,
        rlp_items=rlp_items,
        rlp_items_len=rlp_items_len,
        acc=acc,
        acc_len=acc_len + 1,
        current_index=current_index + 1)
end
