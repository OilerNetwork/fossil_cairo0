from typing import List

def decode_nibbles(input: List[int], skip_nibbles: int = 0) -> List[int]:
    if len(input) == 0: raise Exception("Empty input")

    input_byte_chunked: List[int] = []
    for i in range(0, len(input)):
        word_bytes: List[int] = []
        for j in range(7, 0, -1):
            word_bytes.append(input_byte_chunked[i] >> 8*j)
        input_byte_chunked.extend(word_bytes)

    length = len(input) * 8 * 2
    if skip_nibbles > length: raise Exception("Skip nibbles to large")
    length -= skip_nibbles

    nibbles: List[int] = []

    for i in range(skip_nibbles, skip_nibbles + length):
        (_, r) = divmod(i, 2)
        if r == 0:
           nibbles.append() 


# def verify(proof_rlp: str, root_hash: str, path: List[int]) -> List[int]:
