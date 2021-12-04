import pytest

from utils.helpers import chunk_bytes_input, bytes_to_int_big, ints_array_to_bytes, random_bytes
from utils.benchmarks.extract_from_block_rlp import extractData

@pytest.mark.asyncio
async def test_random():
    block_rlp = random_bytes(1337)

    block_rlp_chunked = chunk_bytes_input(block_rlp)
    block_rlp_formatted = list(map(bytes_to_int_big, block_rlp_chunked))

    for start_byte in range(0, 1200):
        for size in range(1, 66):
            # print("start_byte:", start_byte, "size:", size)
            extracted_words = extractData(block_rlp_formatted, start_byte, size)
            # print(print_ints_array(extracted_words))
            extracted_bytes = ints_array_to_bytes(extracted_words, size)
            expected_bytes = block_rlp[start_byte:start_byte+size]
            assert extracted_bytes == expected_bytes


