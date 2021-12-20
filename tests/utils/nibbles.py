from typing import List
from utils.helpers import words64_to_nibbles, word64_to_nibbles


def merkle_patricia_input_decode(input: List[int], input_len_bytes: int) -> List[List[int]]:
    first_nibble = word64_to_nibbles(input[0], 16)[0]

    skip_nibbles = 0

    if first_nibble == 0:
        skip_nibbles = 2
    elif first_nibble == 1:
        skip_nibbles = 1
    elif first_nibble == 2:
        skip_nibbles = 2
    elif first_nibble == 3:
        skip_nibbles = 1
    else:
        assert False

    nibbles = []
    nibbles.append(word64_to_nibbles(input[0], 8 - skip_nibbles))
    nibbles += words64_to_nibbles(input, input_len_bytes)
    return nibbles