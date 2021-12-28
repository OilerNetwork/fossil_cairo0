from __future__ import annotations
from typing import List, NamedTuple
from enum import Enum


from utils.helpers import chunk_bytes_input, words64_to_nibbles, ints_array_to_bytes, concat_arr


class IntsSequence(NamedTuple):
    values: List[int]
    length: int

class Encoding(Enum):
    LITTLE: str = 'little'
    BIG: str = 'big'

class Data:
    raw_bytes: bytes

    def __init__(self, value: bytes):
        self.raw_bytes = value

    def to_ints(self, encoding: Encoding = Encoding.BIG) -> IntsSequence:
        chunked = chunk_bytes_input(self.raw_bytes)
        ints_array = list(map(lambda chunk: int.from_bytes(chunk, encoding.value), chunked)) 
        return IntsSequence(values=ints_array, length=len(self.raw_bytes))

    def to_hex(self) -> str:
        return "0x" + self.raw_bytes.hex()

    def to_nibbles(self) -> List[int]:
        (words64, size) = self.to_ints()
        return words64_to_nibbles(words64, size)

    @staticmethod
    def from_ints(input: IntsSequence) -> Data:
        raw_bytes = ints_array_to_bytes(input.values, input.length)
        return Data(raw_bytes)

    @staticmethod
    def from_hex(input: str) -> Data:
        prefixed = input[0:2] == '0x'
        return Data(bytes.fromhex(input[2:] if prefixed else input))

    @staticmethod
    def from_bytes(input: bytes) -> Data:
        return Data(input)

    @staticmethod
    def from_nibbles(nibbles: List[int], encoding: Encoding = Encoding.BIG) -> Data:
        single_bytes = []

        assert len(nibbles) % 2 == 0
        if len(nibbles) == 0: return Data(b'')
        
        chunked = [nibbles[i+0:i+2] for i in range(0, len(nibbles), 2)]

        for chunk in chunked:
            single_bytes.append(int.to_bytes((chunk[0] * 2**4) + chunk[1], 1, encoding.value))

        return Data(bytes(concat_arr(single_bytes)))

    def __str__(self) -> str:
        return self.to_hex()