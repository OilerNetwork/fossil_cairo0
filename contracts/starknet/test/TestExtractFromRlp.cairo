%lang starknet
%builtins pedersen range_check ecdsa

from starknet.lib.extract_from_rlp import extractData, is_rlp_list, to_list, getElement, RLPItem, extract_list_values, IntsSequence
from starkware.cairo.common.alloc import alloc

@view
func test_extractData{range_check_ptr}(start_pos: felt, size: felt, rlp_len: felt, rlp: felt*) -> (res_len:felt, res: felt*):
    alloc_locals
    let (local data: IntsSequence) = extractData(
        start_pos=start_pos,
        size=size,
        block_rlp=rlp,
        block_rlp_len=rlp_len)
    return (data.element_size, data.element)
end

@view 
func test_is_rlp_list{range_check_ptr}(pos: felt, rlp_len: felt, rlp: felt*) -> (res: felt):
    return is_rlp_list(pos, rlp, rlp_len)
end

@view
func test_get_element{range_check_ptr}(rlp_len: felt, rlp: felt*, position: felt) -> (res: RLPItem):
    return getElement(rlp, rlp_len, position)
end

@view
func test_extract_list_values{range_check_ptr}(
    rlp_len: felt,
    rlp: felt*,
    rlp_items_data_positions_len: felt,
    rlp_items_data_positions: felt*,
    rlp_items_lenghts_len: felt,
    rlp_items_lenghts: felt*) -> (res_len: felt, res: IntsSequence*):
    alloc_locals

    let (local rlp_items: RLPItem*) = alloc()

    costruct_rlp_items_arr(
        rlp_items_data_positions,
        rlp_items_data_positions_len,
        rlp_items_lenghts,
        rlp_items_lenghts_len,
        acc=rlp_items,
        acc_len=0,
        current_index=0)
    
    let (res, res_len) = extract_list_values(rlp, rlp_len, rlp_items, rlp_items_lenghts_len)
    return (res_len, res)
end

func costruct_rlp_items_arr{range_check_ptr}(
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

    assert acc[current_index] = RLPItem(rlp_items_data_positions[current_index], rlp_items_lenghts[current_index])

    return costruct_rlp_items_arr(
        rlp_items_data_positions=rlp_items_data_positions,
        rlp_items_data_positions_len=rlp_items_data_positions_len,
        rlp_items_lenghts=rlp_items_lenghts,
        rlp_items_lenghts_len=rlp_items_lenghts_len,
        acc=acc,
        acc_len=acc_len,
        current_index=current_index+1)
end 

@view 
func test_to_list{range_check_ptr}(rlp_len: felt, rlp: felt*) -> (data_positions_len: felt, data_positions: felt*, lengths_len: felt, lengths: felt*):
    alloc_locals
    let (local list: RLPItem*, list_len) = to_list(rlp, rlp_len)

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
        current_index=current_index+1)
end