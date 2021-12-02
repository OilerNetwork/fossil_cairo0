from typing import Callable, List
from utils.helpers import ints_array_to_bytes


def getBlockNumberPosition(rlp: List[int]) -> int:
    pos = 448
    pos += nextElementJump(extract_from_block_rlp(rlp, pos, 1)[0])
    return pos

def nextElementJump(prefix: int) -> int:
    if prefix <= 128:
        return 1
    elif prefix <= 183:
        return prefix - 128 + 1
    else:
        raise Exception("not implemented")

def extract_element(rlp: List[int], position: int) -> int:
    value = extract_from_block_rlp(rlp, position, 1)[0]
    
    if value < 128:
        return value.to_bytes(1, "big")
    else:
        element_size = value - 128
        extracted_element = extract_from_block_rlp(rlp, position+1, element_size)
        return ints_array_to_bytes(extracted_element, element_size)

def extract_from_block_rlp(rlp: List[int], start_pos: int, size: int) -> List[int]:
    # print("\n")
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
            final_word_shifted = (rlp[end_word] >> ((8-end_pos) * 8))
            final_word_mask = 2 ** ((end_pos-left_shift)*8) - 1
            new_words.append(final_word_shifted & final_word_mask)

    return new_words

# parent_hash_words = extract_from_block_rlp(input, 32, 32 * 8)
