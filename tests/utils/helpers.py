from eth_typing.encoding import HexStr
from codecs import decode
from typing import Callable, List
from functools import reduce


bytes_to_int: Callable[[bytes], int] = lambda word: int.from_bytes(word, "little")
string_to_byte: Callable[[str], int] = lambda word: int.from_bytes(word.encode("UTF-8"), 'little')
hex_string_to_int: Callable[[HexStr], int] = lambda word: bytes_to_int(bytes.fromhex(word))
concat_arr: Callable[[List[str]], str] = lambda arr: reduce(lambda a, b: a + b, arr)
hex_string_to_byte: Callable[[str], str] = lambda word: decode(word, 'hex_codec')

chunk_input: Callable[[str], List[str]] = lambda input: [input[i+0:i+8] for i in range(0, len(input), 8)]
chunk_hex_input: Callable[[HexStr, bool], List[str]] = lambda input, prefixed=True: [input[i+0:i+8] for i in range(2 if prefixed else 0, len(input), 8)]
chunk_bytes_input: Callable[[bytes], List[bytes]] = lambda input: [input[i+0:i+8] for i in range(0, len(input), 8)]


