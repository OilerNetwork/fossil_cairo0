from secrets import token_bytes
from eth_typing.encoding import HexStr
from typing import Callable, List, Tuple, Union
from functools import reduce
from enum import Enum

from web3 import Web3


class Encoding(Enum):
    LITTLE: str = 'little'
    BIG: str = 'big'


concat_arr: Callable[[List[str]], str] = lambda arr: reduce(lambda a, b: a + b, arr)


def bytes_to_int(word: bytes, encoding: Encoding = Encoding.BIG) -> int:
    return int.from_bytes(word, encoding.value)

bytes_to_int_little: Callable[[bytes], int] = lambda word: int.from_bytes(word, "little")
bytes_to_int_big: Callable[[bytes], int] = lambda word: int.from_bytes(word, "big")

string_to_byte_little: Callable[[str], int] = lambda word: int.from_bytes(word.encode("UTF-8"), 'little')
string_to_byte_big: Callable[[str], int] = lambda word: int.from_bytes(word.encode("UTF-8"), 'big')

hex_string_little_to_int: Callable[[HexStr], int] = lambda word: bytes_to_int_little(bytes.fromhex(word))
hex_string_big_to_int: Callable[[HexStr], int] = lambda word: bytes_to_int_big(bytes.fromhex(word))


chunk_bytes_input: Callable[[bytes], List[bytes]] = lambda input: [input[i+0:i+8] for i in range(0, len(input), 8)]

print_bytes_array: Callable[[List[str]], str] = lambda arr: concat_arr(list(map(lambda a: a.hex()+'\n', arr)))
print_ints_array: Callable[[List[str]], str] = lambda arr: concat_arr(list(map(lambda a: hex(a)+'\n', arr)))

def rlp_string_to_words64(rlp: str, encoding: Encoding = Encoding.BIG) -> List[int]:
    if len(rlp) < 2:
        raise Exception('Rlp string to short')
    prefix = rlp[0:2]
    if prefix == '0x': rlp = rlp[2:]

    chunked = [rlp[i+0:i+16] for i in range(0, len(rlp), 16)]

    return list(map(hex_string_big_to_int if encoding == Encoding.BIG else hex_string_little_to_int, chunked))

def ints_array_to_bytes(ints_array: List[str], size: int) -> str:
    full_words, remainder = divmod(size, 8)

    bytes_array = b''

    for i in range(full_words):
        bytes_array += ints_array[i].to_bytes(8, "big")

    if remainder > 0:
        bytes_array += ints_array[full_words].to_bytes(remainder, "big")
    
    return bytes_array

random_bytes: Callable[[int], bytes] = lambda size: token_bytes(size) 

def word64_to_bytes(word: int, word_len: int) -> List[int]:
    res: List[int] = []
    for i in range(word_len - 1, -1, -1):
        (_, r) = divmod(word >> i * 8, 256)
        res.append(r)
    return res

def word64_to_bytes_recursive_rev(word: int, word_len: int, accumulator = []):
    current_len = word_len - len(accumulator)
    if len(accumulator) == word_len:
        return accumulator
    current_len = word_len - len(accumulator)
    (_, r) = divmod(word >> (word_len - current_len) * 8, 256)
    accumulator.append(r)
    return word64_to_bytes_recursive_rev(word, word_len, accumulator) 

def word64_to_nibbles(word: int, nibbles_len: int, accumulator: List[int] = []) -> List[int]:
    if nibbles_len == 1:
        return accumulator + [word & 0xF]
    return word64_to_nibbles(word >> 4, nibbles_len-1, accumulator) + [(word & 0xF)]

def byte_to_nibbles(input_byte: int) -> Tuple[int, int]:
    nibble_1 = input_byte & 0x0F
    nibble_2 = ((input_byte & 0xF0) >> 4)
    return (nibble_1, nibble_2)

def keccak_words64(input_words64: List[int], input_len: int) -> List[int]:
    return rlp_string_to_words64(Web3.keccak(ints_array_to_bytes(input_words64, input_len)).hex())