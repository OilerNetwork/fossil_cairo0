from eth_typing.encoding import HexStr
from hexbytes.main import HexBytes
from typing import Callable, List
from functools import reduce


bytes_to_int: Callable[[bytes], int] = lambda word: int.from_bytes(word, "little")
hexbyte_to_int: Callable[[HexBytes], int] = lambda word: int(word.hex(), 16)
concat_arr: Callable[[List[str]], str] = lambda arr: reduce(lambda a, b: a + b, arr)
string_to_byte: Callable[[str], int] = lambda word: int.from_bytes(word.encode("UTF-8"), 'little')
hex_string_to_byte: Callable[[str], int] = lambda word: int(word, 16)

chunk_input: Callable[[str], List[str]] = lambda input: [input[i+0:i+8] for i in range(0, len(input), 8)]
chunk_hex_input: Callable[[HexStr, bool], List[str]] = lambda input, prefixed=True: [input[i+0:i+8] for i in range(2 if prefixed else 0, len(input), 8)]
chunk_bytes_input: Callable[[bytes], List[bytes]] = lambda input: [input[i+0:i+4] for i in range(0, len(input), 8)]


