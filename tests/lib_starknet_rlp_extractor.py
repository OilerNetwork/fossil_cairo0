import pytest
import asyncio
from typing import NamedTuple, List

from mocks.blocks import mocked_blocks
from utils.helpers import bytes_to_int, random_bytes
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

    list_input = Data.from_bytes(block_rlp).to_ints()

    is_list_call = await extract_rlp_contract.test_is_rlp_list(0, list_input.length, list_input.values).call()
    is_list = is_list_call.result.res

    assert is_list == 1

@pytest.mark.asyncio
async def test_is_rlp_list_invalid_input(factory):
    starknet, extract_rlp_contract = factory
    
    is_list_call = await extract_rlp_contract.test_is_rlp_list(0, 3, [0x82beef]).call()
    is_list = is_list_call.result.res

    assert is_list == 0

@pytest.mark.asyncio
async def test_get_element(factory):
    starknet, extract_rlp_contract = factory

    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()

    input = Data.from_bytes(block_rlp)

    get_element_call = await extract_rlp_contract.test_get_element(input.to_ints().length, input.to_ints().values, 0).call()
    output = get_element_call.result.res

    expected_output = getElement(input.to_ints(), 0)

    assert output.dataPosition == expected_output.dataPosition
    assert output.length == expected_output.length

@pytest.mark.asyncio
async def test_to_list(factory):
    starknet, extract_rlp_contract = factory

    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = Data.from_bytes(block_header.raw_rlp())

    to_list_call = await extract_rlp_contract.test_to_list(block_rlp.to_ints().length ,block_rlp.to_ints().values).call()
    output = to_list_call.result

    expected = to_list(block_rlp.to_ints())
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

    to_list_call = await extract_rlp_contract.test_to_list(block_rlp.to_ints().length, block_rlp.to_ints().values).call()
    output = to_list_call.result

    expected = to_list(block_rlp.to_ints())
    expected_data_positions = list(map(lambda item: item.dataPosition, expected))
    expected_lengths = list(map(lambda item: item.length, expected))
    expected_first_bytes = list(map(lambda item: item.firstByte, expected))

    assert output.data_positions == expected_data_positions
    assert output.lengths == expected_lengths

    # Extract values:
    extract_values_call = await extract_rlp_contract.test_extract_list_values(
        block_rlp.to_ints().length,
        block_rlp.to_ints().values,
        expected_first_bytes,
        expected_data_positions,
        expected_lengths
    ).call()

    rlp_items = to_list(block_rlp.to_ints())
    rlp_values = extract_list_values(block_rlp.to_ints(), rlp_items)
    
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
    assert output_list_elements[i] == rlp_values[i]



@pytest.mark.asyncio
async def test_extract_list_from_account_rlp_entry(factory):
    starknet, extract_rlp_contract = factory
    input_hex = '0xf8440180a0199c2e6b850bcc9beaea25bf1bacc5741a7aad954d28af9b23f4b53f5404937ba04e36f96ee1667a663dfaac57c4d185a0e369a3a217e0079d49620f34f85d1ac7' 
    input = Data.from_hex(input_hex)

    to_list_call = await extract_rlp_contract.test_to_list(input.to_ints().length, input.to_ints().values).call()
    output = to_list_call.result

    expected = to_list(input.to_ints())
    expected_data_positions = list(map(lambda item: item.dataPosition, expected))
    expected_lengths = list(map(lambda item: item.length, expected))
    expected_first_bytes = list(map(lambda item: item.firstByte, expected))

    assert output.data_positions == expected_data_positions
    assert output.lengths == expected_lengths

    # Extract values:
    extract_values_call = await extract_rlp_contract.test_extract_list_values(
        input.to_ints().length,
        input.to_ints().values,
        expected_first_bytes,
        expected_data_positions,
        expected_lengths
    ).call()

    rlp_items = to_list(input.to_ints())
    rlp_values = extract_list_values(input.to_ints(), rlp_items)
    
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

    for value in rlp_values:
        pass
        # print("Extracted value: ", Data.from_ints(IntsSequence(value.values, value.length)).to_hex())


@pytest.mark.asyncio
async def test_extract_words(factory):
    starknet, extract_rlp_contract = factory
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = Data.from_bytes(block_header.raw_rlp())

    to_list_call = await extract_rlp_contract.test_to_list(block_rlp.to_ints().length, block_rlp.to_ints().values).call()
    output = to_list_call.result

    expected = to_list(block_rlp.to_ints())
    expected_data_positions = list(map(lambda item: item.dataPosition, expected))
    expected_lengths = list(map(lambda item: item.length, expected))

    assert output.data_positions == expected_data_positions
    assert output.lengths == expected_lengths

    rlp_items = to_list(block_rlp.to_ints())

    # Extract values:
    extract_data_call = await extract_rlp_contract.test_extractData(
        rlp_items[0].dataPosition,
        rlp_items[0].length,
        block_rlp.to_ints().length,
        block_rlp.to_ints().values
    ).call()

    extract_data_result = extract_data_call.result.res

@pytest.mark.asyncio
async def test_extract_element(factory):
    starknet, extract_rlp_contract = factory

    input = Data.from_hex('0x2A').to_ints()

    extract_element_call = await extract_rlp_contract.test_extractElement(0, input.length, input.values).call()
    result = extract_element_call.result
    assert result.res == [42]


@pytest.mark.asyncio
async def test_random(factory):
    starknet, extract_rlp_contract = factory
    for length in range (0, 35):
        input = Data.from_bytes(random_bytes(length))
        for start_byte in range(0, length):
            for size in range(0, length-start_byte+1):
                # print(input.to_hex())
                # print(input.to_ints().values)
                extracted_words_call = await extract_rlp_contract.test_extractData(start_byte, size, input.to_ints().length, input.to_ints().values).call()
                output = Data.from_ints(IntsSequence(extracted_words_call.result.res, extracted_words_call.result.res_len_bytes))
                expected_output = Data.from_bytes(input.to_bytes()[start_byte:start_byte+size])
                if output != expected_output:
                    print(input.to_hex())
                    print(output.to_hex())
                    print(expected_output.to_hex())
                assert output == expected_output


