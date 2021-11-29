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

ints_array_to_bytes: Callable[[List[str]], str] = lambda arr: concat_arr(map(lambda a: bytes.fromhex(hex(a)[2:] if len(hex(a)[2:]) % 2 == 0 else "0"+hex(a)[2:]), arr))