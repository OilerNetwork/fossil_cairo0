import pytest
from utils.helpers import ints_array_to_bytes

from utils.rlp import extractData, count_items, to_list, extract_list_values
from utils.types import Data
from utils.helpers import random_bytes, ints_array_to_bytes, bytes_to_int

from mocks.trie_proofs import trie_proofs


bytes_to_int_big = lambda word: bytes_to_int(word)

@pytest.mark.asyncio
async def test_count_items():
    input = trie_proofs[0]['accountProof'][0]

    expected_items_count = 17
    items_count = count_items(Data.from_hex(input).to_ints(), 0)

    assert expected_items_count == items_count


@pytest.mark.asyncio
async def test_to_list():
    input = trie_proofs[0]['accountProof'][0]
    items = to_list(Data.from_hex(input).to_ints())

    assert len(items) == 17

@pytest.mark.asyncio
async def test_to_list_values():
    input = Data.from_hex(trie_proofs[0]['accountProof'][7])
    items = to_list(input.to_ints())
    for item in items:
        value = extractData(input.to_ints(), item.dataPosition, item.length)
        # print(ints_array_to_bytes(value, item.length).hex())

@pytest.mark.asyncio
async def test_rlp_account_entry():
    input_hex = '0xf8440180a0199c2e6b850bcc9beaea25bf1bacc5741a7aad954d28af9b23f4b53f5404937ba04e36f96ee1667a663dfaac57c4d185a0e369a3a217e0079d49620f34f85d1ac7'
    input = Data.from_hex(input_hex)

    code_hash_element = extractData(input.to_ints(), 38, 32)


@pytest.mark.asyncio
async def test_random():
    for length in range (1, 100):
        input = Data.from_bytes(random_bytes(length))
        for start_byte in range(0, length):
            for size in range(0, length-start_byte+1):
                # print(f"{length}: {start_byte}-{start_byte+size}")
                output = Data.from_ints(extractData(input.to_ints(), start_byte, size))
                expected_output = Data.from_bytes(input.to_bytes()[start_byte:start_byte+size])
                if output != expected_output:
                    print(input.to_hex())
                    print(output.to_hex())
                    print(expected_output.to_hex())
                assert output == expected_output
