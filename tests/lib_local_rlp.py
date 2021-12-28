import pytest

from utils.rlp import extractData, count_items, to_list, extract_list_values
from utils.types import Data

from mocks.trie_proofs import trie_proofs


@pytest.mark.asyncio
async def test_count_items():
    input = trie_proofs[0]['accountProof'][0]

    expected_items_count = 17
    items_count = count_items(Data.from_hex(input).to_ints().values, 0)

    assert expected_items_count == items_count


@pytest.mark.asyncio
async def test_to_list():
    input = trie_proofs[0]['accountProof'][0]
    items = to_list(Data.from_hex(input).to_ints().values)

    assert len(items) == 17

@pytest.mark.asyncio
async def test_to_list_values():
    input = trie_proofs[0]['accountProof'][7]
    items = to_list(Data.from_hex(input).to_ints().values)
    for item in items:
        value = extractData(input, item.dataPosition, item.length)
        # print(ints_array_to_bytes(value, item.length).hex())

# @pytest.mark.asyncio
# async def test_random():
#     block_rlp = random_bytes(1337)

#     block_rlp_chunked = chunk_bytes_input(block_rlp)
#     block_rlp_formatted = list(map(bytes_to_int_big, block_rlp_chunked))

#     for start_byte in range(0, 1200):
#         for size in range(1, 66):
#             extracted_words = extractData(block_rlp_formatted, start_byte, size)
#             extracted_bytes = ints_array_to_bytes(extracted_words, size)
#             expected_bytes = block_rlp[start_byte:start_byte+size]
#             assert extracted_bytes == expected_bytes
