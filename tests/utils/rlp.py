from typing import List, NamedTuple


class RLPElement(NamedTuple):
    element: List[int]
    nextElementPosition: int

class RLPLength(NamedTuple):
    value: int
    dataPosition: int

# Returns length of data and position of data
# if length is -1 then data is at the returned position
def getElementLength(rlp: List[int], position: int) -> RLPLength:
    #print(extractData(rlp, position, 16))
    firstByte = extractData(rlp, position, 1)[0]

    if firstByte <= 127:
        return RLPLength(-1, position)
    if firstByte <= 183:
        return RLPLength(firstByte - 128, position+1)
    if firstByte <= 191:
        lengthOfLength = firstByte - 183
        length = extractData(rlp, position+1, lengthOfLength)[0]
        return RLPLength(length, position + lengthOfLength)
    if firstByte <= 247:
        return  RLPLength(firstByte - 192, position+1)
    lengthOfLength = firstByte - 247
    length = extractData(rlp, position+1, lengthOfLength)[0]
    return RLPLength(length, position + lengthOfLength)

def isRlpList(rlp: List[int], position: int) -> bool:
    firstByte = extractData(rlp, position, 1)[0]
    return firstByte >= 192

# returns RLPElement - list of ints, and a position of next element
def extractElement(rlp: List[int], position: int) -> RLPElement:
    length, dataPosition = getElementLength(rlp, position)

    if length == -1:
        return RLPElement(extractData(rlp, dataPosition, 1), dataPosition+1)

    if length == 0:
        return RLPElement([], dataPosition)

    return RLPElement(extractData(rlp, dataPosition, length), dataPosition + length)

# returns next element position
def jumpOverElement(rlp: List[int], position: int) -> int:
    length, dataPosition = getElementLength(rlp, position)

    if length == -1:
        return position+1
    else:
        return dataPosition + length
    
def extractData(rlp: List[int], start_pos: int, size: int) -> List[int]:
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

    return new_words


def count_items(rlp: List[int], pos: int = 0) -> int:
    count = 0
    (payload_len, payload_pos) = getElementLength(rlp, pos)

    payload_end = payload_pos + payload_len
    curr_element_pos = payload_pos

    while curr_element_pos < payload_end:
        curr_element_pos = jumpOverElement(rlp, curr_element_pos)
        count += 1
    return count

def to_list(rlp: List[int]) -> List[List[int]]:
    return []
