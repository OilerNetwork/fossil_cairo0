from typing import List
from rlp import encode, decode
from eth_utils import decode_hex


def encode_proof(proof: List[str]) -> str:
    input = list(map(lambda i: decode(decode_hex(i)), proof))
    return "0x" + encode(input).hex()


