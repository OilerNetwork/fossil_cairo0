%lang starknet
%builtins pedersen range_check ecdsa

from starknet.lib.extract_from_rlp import extract_data, is_rlp_list, to_list, getElement, extract_list_values, extractElement
from starknet.lib.concat_arr import concat_arr
from starknet.types import IntsSequence, RLPItem

from starkware.cairo.common.alloc import alloc
from starkware.cairo.common.memcpy import memcpy


@view
func test_extractData{range_check_ptr}(start_pos: felt, size: felt, rlp_len_bytes: felt, rlp_len: felt, rlp: felt*) -> (res_len_bytes: felt, res_len:felt, res: felt*):
    alloc_locals
    local input: IntsSequence = IntsSequence(rlp, rlp_len, rlp_len_bytes)
    let (local data: IntsSequence) = extract_data(
        start_pos=start_pos,
        size=size,
        rlp=input)
    return (data.element_size_bytes, data.element_size_words, data.element)
end

@view
func test_extractElement{range_check_ptr}(pos: felt, rlp_len_bytes: felt, rlp_len: felt, rlp: felt*) -> (res_len_bytes: felt, res_len:felt, res: felt*):
    alloc_locals
    local input: IntsSequence = IntsSequence(rlp, rlp_len, rlp_len_bytes)
    let (local result: IntsSequence) = extractElement(input, pos)
    return (result.element_size_bytes, result.element_size_words, result.element)
end

@view 
func test_is_rlp_list{range_check_ptr}(pos: felt, rlp_len_bytes: felt, rlp_len: felt, rlp: felt*) -> (res: felt):
    alloc_locals
    local input: IntsSequence = IntsSequence(rlp, rlp_len, rlp_len_bytes)
    return is_rlp_list(pos, input)
end

@view
func test_get_element{range_check_ptr}(rlp_len_bytes: felt, rlp_len: felt, rlp: felt*, position: felt) -> (res: RLPItem):
    alloc_locals
    local input: IntsSequence = IntsSequence(rlp, rlp_len, rlp_len_bytes)
    return getElement(input, position)
end

@view
func test_extract_list_values{range_check_ptr}(
    rlp_len_bytes: felt,
    rlp_len: felt,
    rlp: felt*,
    rlp_items_first_bytes_len: felt,
    rlp_items_first_bytes: felt*,
    rlp_items_data_positions_len: felt,
    rlp_items_data_positions: felt*,
    rlp_items_lenghts_len: felt,
    rlp_items_lenghts: felt*) -> (
        flattened_list_elements_len: felt,
        flattened_list_elements: felt*,
        flattened_list_sizes_words_len: felt,
        flattened_list_sizes_words: felt*,
        flattened_list_sizes_bytes_len: felt,
        flattened_list_sizes_bytes: felt*):
    alloc_locals

    # flattened_list_elements: felt*
    # flattened_list_sizes: felt*

    let (local rlp_items: RLPItem*) = alloc()

    costruct_rlp_items_arr(
        rlp_items_first_bytes,
        rlp_items_first_bytes_len,
        rlp_items_data_positions,
        rlp_items_data_positions_len,
        rlp_items_lenghts,
        rlp_items_lenghts_len,
        acc=rlp_items,
        acc_len=0,
        current_index=0)

    local rlp_input: IntsSequence = IntsSequence(rlp, rlp_len, rlp_len_bytes) 
    let (res, res_len) = extract_list_values(rlp_input, rlp_items, rlp_items_lenghts_len)

    let (local flattened_list_elements: felt*) = alloc()
    let (local flattened_list_sizes_words: felt*) = alloc()
    let (local flattened_list_sizes_bytes: felt*) = alloc()
    
    let (elements_acc_len, sizes_words_acc_len, sizes_bytes_acc_len) = flatten_ints_sequence_array(
        arr=res,
        arr_len=res_len,
        elements_acc=flattened_list_elements,
        elements_acc_len=0,
        sizes_words_acc=flattened_list_sizes_words,
        sizes_words_acc_len=0,
        sizes_bytes_acc=flattened_list_sizes_bytes,
        sizes_bytes_acc_len=0,
        current_index=0)
    return (
        elements_acc_len,
        flattened_list_elements,
        sizes_words_acc_len,
        flattened_list_sizes_words,
        sizes_bytes_acc_len,
        flattened_list_sizes_bytes)
end

func flatten_ints_sequence_array{range_check_ptr}(
    arr: IntsSequence*,
    arr_len: felt,
    elements_acc: felt*,
    elements_acc_len: felt,
    sizes_words_acc: felt*,
    sizes_words_acc_len: felt,
    sizes_bytes_acc: felt*,
    sizes_bytes_acc_len: felt,
    current_index: felt
    ) -> (elements_acc_length: felt, sizes_words_acc_len: felt, sizes_bytes_acc_len: felt):
    alloc_locals
    if current_index == arr_len:
        return (elements_acc_len, sizes_words_acc_len, sizes_bytes_acc_len)
    end

    # Handle elements
    memcpy(elements_acc + elements_acc_len, arr[current_index].element, arr[current_index].element_size_words)

    # Handle sizes
    assert sizes_words_acc[current_index] = arr[current_index].element_size_words
    assert sizes_bytes_acc[current_index] = arr[current_index].element_size_bytes

    return flatten_ints_sequence_array(
        arr=arr,
        arr_len=arr_len,
        elements_acc=elements_acc,
        elements_acc_len=elements_acc_len + arr[current_index].element_size_words,
        sizes_words_acc=sizes_words_acc,
        sizes_words_acc_len=sizes_words_acc_len + 1,
        sizes_bytes_acc=sizes_bytes_acc,
        sizes_bytes_acc_len=sizes_bytes_acc_len + 1,
        current_index=current_index + 1)
end

func costruct_rlp_items_arr{range_check_ptr}(
    rlp_items_first_bytes: felt*,
    rlp_items_first_bytes_len: felt,
    rlp_items_data_positions: felt*,
    rlp_items_data_positions_len: felt,
    rlp_items_lenghts: felt*,
    rlp_items_lenghts_len: felt,
    acc: RLPItem*,
    acc_len: felt,
    current_index: felt
    ):
    if current_index == rlp_items_data_positions_len:
        return ()
    end

    assert acc[current_index] = RLPItem(rlp_items_first_bytes[current_index], rlp_items_data_positions[current_index], rlp_items_lenghts[current_index])

    return costruct_rlp_items_arr(
        rlp_items_first_bytes=rlp_items_first_bytes,
        rlp_items_first_bytes_len=rlp_items_first_bytes_len,
        rlp_items_data_positions=rlp_items_data_positions,
        rlp_items_data_positions_len=rlp_items_data_positions_len,
        rlp_items_lenghts=rlp_items_lenghts,
        rlp_items_lenghts_len=rlp_items_lenghts_len,
        acc=acc,
        acc_len=acc_len,
        current_index=current_index + 1)
end 

@view 
func test_to_list{range_check_ptr}(rlp_len_bytes: felt, rlp_len: felt, rlp: felt*) -> (data_positions_len: felt, data_positions: felt*, lengths_len: felt, lengths: felt*):
    alloc_locals
    local input: IntsSequence = IntsSequence(rlp, rlp_len, rlp_len_bytes) 
    let (local list: RLPItem*, list_len) = to_list(input)

    let (local data_positions: felt*) = alloc()
    let (local lengths: felt*) = alloc()

    decostruct_rlp_items_arr(list, list_len, data_positions, 0, lengths, 0, 0)

    return (list_len, data_positions, list_len, lengths)
end

func decostruct_rlp_items_arr{range_check_ptr}(
    list: RLPItem*,
    list_len: felt,
    data_positions_acc: felt*,
    data_positions_acc_len: felt,
    lengths_acc: felt*,
    lengths_acc_len: felt,
    current_index: felt
    ):
    if current_index == list_len:
        return ()
    end

    assert data_positions_acc[current_index] = list[current_index].dataPosition
    assert lengths_acc[current_index] = list[current_index].length

    return decostruct_rlp_items_arr(
        list=list,
        list_len=list_len,
        data_positions_acc=data_positions_acc,
        data_positions_acc_len=data_positions_acc_len,
        lengths_acc=lengths_acc,
        lengths_acc_len=lengths_acc_len,
        current_index=current_index + 1)
end