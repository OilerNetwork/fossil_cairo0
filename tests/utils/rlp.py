from typing import List, NamedTuple
from utils.types import IntsSequence


class RLPItem(NamedTuple):
    dataPosition: int
    length: int

# Returns length of data and position of data
# if length is -1 then data is at the returned position
def getElement(rlp: List[int], position: int) -> RLPItem:
    #print(extractData(rlp, position, 16))
    firstByte = extractData(rlp, position, 1).values[0]

    if firstByte <= 127:
        return RLPItem(position, 1)

    if firstByte <= 183:
        return RLPItem(position + 1, firstByte - 128)

    if firstByte <= 191:
        lengthOfLength = firstByte - 183
        length = extractData(rlp, position + 1, lengthOfLength).values[0]
        return RLPItem(position + 1 + lengthOfLength, length)

    if firstByte <= 247:
        return  RLPItem(position + 1, firstByte - 192)

    lengthOfLength = firstByte - 247
    length = extractData(rlp, position + 1, lengthOfLength).values[0]
    return RLPItem(position + 1 + lengthOfLength, length)


def isRlpList(rlp: List[int], position: int) -> bool:
    firstByte = extractData(rlp, position, 1).values[0]
    return firstByte >= 192

# returns RLPElement - list of ints, and a position of next element
def extractElement(rlp: List[int], position: int) -> IntsSequence:
    dataPosition, length = getElement(rlp, position)

    if length == 0:
        return IntsSequence([], dataPosition)

    return extractData(rlp, dataPosition, length)

# returns next element position
def jumpOverElement(rlp: List[int], position: int) -> int:
    dataPosition, length = getElement(rlp, position)
    return dataPosition + length
    
def extractData(rlp: List[int], start_pos: int, size: int) -> IntsSequence:
    start_word, left_shift = divmod(start_pos, 8)
    end_word, end_pos = divmod(start_pos + size, 8)

    if end_pos == 0:
        end_pos = 8
        end_word -= 1

    right_shift = 8 - left_shift
    full_words, remainder = divmod(size, 8)

    new_words: List[int] = []
    # We exclude end_word for purpose:
    for i in range(start_word, start_word + full_words):
        left_part = rlp[i] << left_shift * 8
        right_part = rlp[i + 1] >> right_shift * 8
        new_words.append((left_part + right_part) & (2**(64)-1))

    # Process last word:
    if remainder != 0:
        if remainder + left_shift > 8:
            #process two words
            left_part = rlp[end_word - 1] << left_shift * 8
            right_part = rlp[end_word] >> right_shift * 8
            final_word = left_part + right_part

            final_word_shifted = (final_word >> ((8 - remainder) * 8))
            final_word_mask = 2 ** (remainder * 8) - 1
            new_words.append(final_word_shifted & final_word_mask)
        else:
            #process one word
            final_word_shifted = rlp[end_word] >> ((8-end_pos) * 8)
            final_word_mask = 2 ** ((end_pos-left_shift)*8) - 1
            new_words.append(final_word_shifted & final_word_mask)

    return IntsSequence(values=new_words, length=size)


def count_items(rlp: List[int], pos: int = 0) -> int:
    count = 0
    (payload_pos, payload_len) = getElement(rlp, pos)

    payload_end = payload_pos + payload_len
    curr_element_pos = payload_pos

    while curr_element_pos < payload_end:
        curr_element_pos = jumpOverElement(rlp, curr_element_pos)
        count += 1
    return count

def to_list(rlp: List[int]) -> List[RLPItem]:
    assert isRlpList(rlp, 0)

    res: List[RLPItem] = []

    (payload_pos, payload_len) = getElement(rlp, 0)
    payload_end = payload_pos + payload_len
    next_element_pos = payload_pos

    while next_element_pos < payload_end:
        (element_pos, element_len) = getElement(rlp, next_element_pos)
        next_element_pos = element_pos + element_len
        res.append(RLPItem(element_pos, element_len))
    return res

def extract_list_values(rlp: List[int], rlp_items: List[RLPItem]) -> List[IntsSequence]:
    res = []
    for rlp_item in rlp_items:
        res.append(extractData(rlp, rlp_item.dataPosition, rlp_item.length))
    return res
