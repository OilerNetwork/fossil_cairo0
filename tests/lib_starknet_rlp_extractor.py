import pytest
import asyncio
from typing import NamedTuple, List

from mocks.blocks import mocked_blocks
from utils.helpers import chunk_bytes_input, bytes_to_int, ints_array_to_bytes, random_bytes
from utils.block_header import build_block_header

from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.testing.starknet import Starknet

from utils.types import Data
from utils.rlp import to_list, getElement, extract_list_values, IntsSequence

class TestsDeps(NamedTuple):
    starknet: Starknet
    extract_rlp_contract: StarknetContract

@pytest.fixture(scope='module')
def event_loop():
    return asyncio.new_event_loop()

async def setup():
    starknet = await Starknet.empty()
    extract_rlp_contract = await starknet.deploy(source="contracts/starknet/test/TestExtractFromRlp.cairo", cairo_path=["contracts"])
    return TestsDeps(
        starknet=starknet,
        extract_rlp_contract=extract_rlp_contract
    )

@pytest.fixture(scope='module')
async def factory():
    return await setup()


bytes_to_int_big = lambda word: bytes_to_int(word)


@pytest.mark.asyncio
async def test_is_rlp_list_valid_input(factory):
    starknet, extract_rlp_contract = factory
    
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()

    is_list_call = await extract_rlp_contract.test_is_rlp_list(0, list(map(bytes_to_int_big, chunk_bytes_input(block_rlp)))).call()
    is_list = is_list_call.result.res

    assert is_list == 1

@pytest.mark.asyncio
async def test_is_rlp_list_invalid_input(factory):
    starknet, extract_rlp_contract = factory
    
    is_list_call = await extract_rlp_contract.test_is_rlp_list(0, [0x82beef]).call()
    is_list = is_list_call.result.res

    assert is_list == 0

@pytest.mark.asyncio
async def test_get_element(factory):
    starknet, extract_rlp_contract = factory

    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()

    input = Data.from_bytes(block_rlp)

    get_element_call = await extract_rlp_contract.test_get_element(input.to_ints().values, 0).call()
    output = get_element_call.result.res

    expected_output = getElement(input.to_ints().values, 0)

    assert output.dataPosition == expected_output.dataPosition
    assert output.length == expected_output.length

@pytest.mark.asyncio
async def test_to_list(factory):
    starknet, extract_rlp_contract = factory

    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = Data.from_bytes(block_header.raw_rlp())

    to_list_call = await extract_rlp_contract.test_to_list(block_rlp.to_ints().values).call()
    output = to_list_call.result

    expected = to_list(block_rlp.to_ints().values)
    expected_data_positions = list(map(lambda item: item.dataPosition, expected))
    expected_lengths = list(map(lambda item: item.length, expected))

    assert output.data_positions == expected_data_positions
    assert output.lengths == expected_lengths

@pytest.mark.asyncio
async def test_extract_list_values(factory):
    starknet, extract_rlp_contract = factory
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = Data.from_bytes(block_header.raw_rlp())

    to_list_call = await extract_rlp_contract.test_to_list(block_rlp.to_ints().values).call()
    output = to_list_call.result

    expected = to_list(block_rlp.to_ints().values)
    expected_data_positions = list(map(lambda item: item.dataPosition, expected))
    expected_lengths = list(map(lambda item: item.length, expected))

    assert output.data_positions == expected_data_positions
    assert output.lengths == expected_lengths

    # Extract values:
    extract_values_call = await extract_rlp_contract.test_extract_list_values(
        block_rlp.to_ints().values,
        expected_data_positions,
        expected_lengths
    ).call()

    rlp_items = to_list(block_rlp.to_ints().values)
    rlp_values = extract_list_values(block_rlp.to_ints().values, rlp_items)
    
    output_list_elements_flat = extract_values_call.result.flattened_list_elements
    output_list_elements_sizes_words = extract_values_call.result.flattened_list_sizes_words
    output_list_elements_sizes_bytes = extract_values_call.result.flattened_list_sizes_bytes

    offset = 0
    output_list_elements: List[IntsSequence] = []
    for i in range(0 , len(output_list_elements_sizes_words)):
        size_words = output_list_elements_sizes_words[i]
        size_bytes = output_list_elements_sizes_bytes[i]
        output_list_elements.append(IntsSequence(output_list_elements_flat[offset:offset+size_words], size_bytes))
        offset += size_words

    assert output_list_elements == rlp_values


@pytest.mark.asyncio
async def test_extract_words(factory):
    starknet, extract_rlp_contract = factory
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = Data.from_bytes(block_header.raw_rlp())

    to_list_call = await extract_rlp_contract.test_to_list(block_rlp.to_ints().values).call()
    output = to_list_call.result

    expected = to_list(block_rlp.to_ints().values)
    expected_data_positions = list(map(lambda item: item.dataPosition, expected))
    expected_lengths = list(map(lambda item: item.length, expected))

    assert output.data_positions == expected_data_positions
    assert output.lengths == expected_lengths

    rlp_items = to_list(block_rlp.to_ints().values)

    print(rlp_items[0])

    # Extract values:
    extract_data_call = await extract_rlp_contract.test_extractData(
        rlp_items[0].dataPosition,
        rlp_items[0].length,
        block_rlp.to_ints().values
    ).call()

    extract_data_result = extract_data_call.result.res

    print(extract_data_result)


@pytest.mark.asyncio
async def test_random(factory):
    starknet, extract_rlp_contract = factory
    block_rlp = random_bytes(1337)
    # print("\n0x" + block_rlp.hex())

    block_rlp_chunked = chunk_bytes_input(block_rlp)
    block_rlp_formatted = list(map(bytes_to_int_big, block_rlp_chunked))

    for start_byte in range(0, 20):
        for size in range(1, 35):
            extracted_words_call = await extract_rlp_contract.test_extractData(start_byte, size, block_rlp_formatted).call()
            extracted_words = extracted_words_call.result.res
            extracted_bytes = ints_array_to_bytes(IntsSequence(extracted_words, size))
            expected_bytes = block_rlp[start_byte:start_byte+size]
            assert extracted_bytes == expected_bytes

