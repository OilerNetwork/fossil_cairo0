from brownie import accounts

from mocks.blocks import mocked_blocks
from utils.helpers import chunk_bytes_input, bytes_to_int_big

def test_format_words64_deploys(TestFormatWords64):
    format_words64 = accounts[0].deploy(TestFormatWords64)
    assert int(format_words64.address, 16) > 0

def test_format_words64_from_bytes32(TestFormatWords64):
    format_words64 = accounts[0].deploy(TestFormatWords64)

    input = mocked_blocks[0]['parentHash'].hex()
    bytes32_to_words64 = format_words64.fromBytes32(input)

    chunked_message = chunk_bytes_input(bytearray.fromhex(mocked_blocks[0]["parentHash"].hex()[2:]))
    expected_words = list(map(bytes_to_int_big, chunked_message))
    expected_words_hex = list(map(lambda x: hex(x), expected_words))

    assert bytes32_to_words64 == expected_words_hex
    