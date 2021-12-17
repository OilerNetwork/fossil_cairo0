import pytest

from utils.helpers import chunk_bytes_input, bytes_to_int, ints_array_to_bytes, random_bytes, rlp_string_to_words64
from utils.rlp import extractData, count_items, to_list, extract_list_values

from mocks.trie_proofs import trie_proofs



bytes_to_int_big = lambda word: bytes_to_int(word)


@pytest.mark.asyncio
async def test_count_items():
    input = trie_proofs[0]['accountProof'][0]
    input_words64 = rlp_string_to_words64(input)

    expected_items_count = 17
    items_count = count_items(input_words64, 0)

    assert expected_items_count == items_count


@pytest.mark.asyncio
async def test_to_list():
    input = rlp_string_to_words64(trie_proofs[0]['accountProof'][0])
    items = to_list(input)

    print(items)

    assert len(items) == 17

@pytest.mark.asyncio
async def test_to_list_values():
    input = rlp_string_to_words64(trie_proofs[0]['accountProof'][0])
    items = to_list(input)
    values = extract_list_values(input, items)
    print(values)


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


