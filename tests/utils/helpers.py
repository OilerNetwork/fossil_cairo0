from secrets import token_bytes
from eth_typing.encoding import HexStr
from typing import Callable, List
from functools import reduce


bytes_to_int_little: Callable[[bytes], int] = lambda word: int.from_bytes(word, "little")
bytes_to_int_big: Callable[[bytes], int] = lambda word: int.from_bytes(word, "big")

string_to_byte_little: Callable[[str], int] = lambda word: int.from_bytes(word.encode("UTF-8"), 'little')
string_to_byte_big: Callable[[str], int] = lambda word: int.from_bytes(word.encode("UTF-8"), 'big')

hex_string_little_to_int: Callable[[HexStr], int] = lambda word: bytes_to_int_little(bytes.fromhex(word))
hex_string_big_to_int: Callable[[HexStr], int] = lambda word: bytes_to_int_big(bytes.fromhex(word))

concat_arr: Callable[[List[str]], str] = lambda arr: reduce(lambda a, b: a + b, arr)

chunk_bytes_input: Callable[[bytes], List[bytes]] = lambda input: [input[i+0:i+8] for i in range(0, len(input), 8)]

print_bytes_array: Callable[[List[str]], str] = lambda arr: concat_arr(list(map(lambda a: a.hex()+'\n', arr)))

print_ints_array: Callable[[List[str]], str] = lambda arr: concat_arr(list(map(lambda a: hex(a)+'\n', arr)))

def ints_array_to_bytes(ints_array: List[str], size: int) -> str:
    full_words, remainder = divmod(size, 8);

    bytes_array = b''

    for i in range(full_words):
        bytes_array += ints_array[i].to_bytes(8, "big")

    if remainder > 0:
        bytes_array += ints_array[full_words].to_bytes(remainder, "big")
    
    return bytes_array

random_bytes: Callable[[int], bytes] = lambda size: token_bytes(size) 

# TODO does not work
def word64_to_bytes(word: int) -> List[int]:
    word_bytes: List[int] = []
    for i in range(7, -1, -1):
        left_shift = 7 - i
        word_bytes.append((word << left_shift) >> 64)
    return word_bytes
