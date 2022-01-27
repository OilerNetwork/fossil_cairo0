from typing import List, NamedTuple
from utils.types import IntsSequence


class RLPItem(NamedTuple):
    firstByte: int
    dataPosition: int
    length: int

# Returns length of data and position of data
# if length is -1 then data is at the returned position
def getElement(rlp: IntsSequence, position: int) -> RLPItem:
    firstByte = extractData(rlp, position, 1).values[0]

    if firstByte <= 127:
        return RLPItem(firstByte, position, 1)

    if firstByte <= 183:
        return RLPItem(firstByte, position + 1, firstByte - 128)

    if firstByte <= 191:
        lengthOfLength = firstByte - 183
        length = extractData(rlp, position + 1, lengthOfLength).values[0]
        return RLPItem(firstByte, position + 1 + lengthOfLength, length)

    if firstByte <= 247:
        return  RLPItem(firstByte, position + 1, firstByte - 192)

    lengthOfLength = firstByte - 247
    length = extractData(rlp, position + 1, lengthOfLength).values[0]
    return RLPItem(firstByte, position + 1 + lengthOfLength, length)


def isRlpList(rlp: IntsSequence, position: int) -> bool:
    firstByte = extractData(rlp, position, 1).values[0]
    return firstByte >= 192

def isRlpList_RlpItem(rlp: IntsSequence, item: RLPItem) -> bool:
    firstByte = item.firstByte
    return firstByte >= 192

# returns RLPElement - list of ints, and a position of next element
def extractElement(rlp: IntsSequence, position: int) -> IntsSequence:
    _ ,dataPosition, length = getElement(rlp, position)

    if length == 0:
        return IntsSequence([], dataPosition)

    return extractData(rlp, dataPosition, length)

# returns next element position
def jumpOverElement(rlp: IntsSequence, position: int) -> int:
    _, dataPosition, length = getElement(rlp, position)
    return dataPosition + length

def extractDataFromRLPItem(rlp: IntsSequence, rlpItem: RLPItem) -> IntsSequence:
    return extractData(rlp, rlpItem.dataPosition, rlpItem.length)

def extractData(rlp: IntsSequence, start_pos: int, size: int) -> IntsSequence:
    start_word, left_shift = divmod(start_pos, 8)
    end_word, end_pos = divmod(start_pos + size, 8)

    if end_pos == 0:
        end_pos = 8
        end_word -= 1

    full_words, remainder = divmod(size, 8)

    _, last_rlp_word_len_tmp = divmod(rlp.length, 8)
    if last_rlp_word_len_tmp == 0:
        last_rlp_word_len = 8
    else:
        last_rlp_word_len = last_rlp_word_len_tmp

    right_shift = 8 - left_shift
    lastword_right_shift = last_rlp_word_len - left_shift

    new_words: List[int] = []
    # We exclude end_word for purpose:
    for i in range(start_word, start_word + full_words):
        left_part = rlp.values[i] << left_shift * 8
        if i == len(rlp.values) - 2:
            if (lastword_right_shift < 0):
                right_part = rlp.values[i + 1] << -lastword_right_shift * 8
            else:
                right_part = rlp.values[i + 1] >> lastword_right_shift * 8
        else:                
            if i == len(rlp.values) - 1:
                right_part = 0
            else:
                right_part = rlp.values[i + 1] >> right_shift * 8
        new_words.append((left_part + right_part) & (2**(64)-1))

    # Process last word:
    if remainder != 0:
        if remainder + left_shift > 8:
            #process two words
            left_part = rlp.values[end_word - 1] << left_shift * 8

            if end_word == len(rlp.values) - 1:
                if (lastword_right_shift < 0):
                    right_part = rlp.values[end_word] << -lastword_right_shift * 8
                else:
                    right_part = rlp.values[end_word] >> lastword_right_shift * 8
            else:
                right_part = rlp.values[end_word] >> right_shift * 8

            final_word = left_part + right_part

            final_word_shifted = (final_word >> ((8 - remainder) * 8))
            final_word_mask = 2 ** (remainder * 8) - 1
            new_words.append(final_word_shifted & final_word_mask)
        else:
            #process one word
            if end_word == len(rlp.values) - 1:
                final_word_shifted = rlp.values[end_word] >> ((last_rlp_word_len-end_pos) * 8)
            else:
                final_word_shifted = rlp.values[end_word] >> ((8-end_pos) * 8)
            final_word_mask = 2 ** ((end_pos-left_shift)*8) - 1
            new_words.append(final_word_shifted & final_word_mask)

    return IntsSequence(values=new_words, length=size)


def count_items(rlp: IntsSequence, pos: int = 0) -> int:
    count = 0
    (_, payload_pos, payload_len) = getElement(rlp, pos)

    payload_end = payload_pos + payload_len
    curr_element_pos = payload_pos

    while curr_element_pos < payload_end:
        curr_element_pos = jumpOverElement(rlp, curr_element_pos)
        count += 1
    return count

def to_list(rlp: IntsSequence) -> List[RLPItem]:
    assert isRlpList(rlp, 0)

    res: List[RLPItem] = []

    (_, payload_pos, payload_len) = getElement(rlp, 0)
    payload_end = payload_pos + payload_len
    next_element_pos = payload_pos

    while next_element_pos < payload_end:
        (firstByte, element_pos, element_len) = getElement(rlp, next_element_pos)
        next_element_pos = element_pos + element_len
        res.append(RLPItem(firstByte, element_pos, element_len))
    return res

def extract_list_values(rlp: IntsSequence, rlp_items: List[RLPItem]) -> List[IntsSequence]:
    res = []
    for rlp_item in rlp_items:
        res.append(extractData(rlp, rlp_item.dataPosition, rlp_item.length))
    return res
