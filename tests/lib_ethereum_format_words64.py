from brownie import accounts

from mocks.blocks import mocked_blocks
from utils.helpers import bytes_to_int
from utils.types import Data

bytes_to_int_big = lambda word: bytes_to_int(word)


def test_format_words64_deploys(TestFormatWords64):
    format_words64 = accounts[0].deploy(TestFormatWords64)
    assert int(format_words64.address, 16) > 0

def test_format_words64_from_bytes32(TestFormatWords64):
    format_words64 = accounts[0].deploy(TestFormatWords64)

    input = mocked_blocks[0]['parentHash'].hex()
    bytes32_to_words64 = format_words64.fromBytes32(input)

    expected_words = Data.from_hex(mocked_blocks[0]["parentHash"].hex()).to_ints().values
    expected_words_hex = list(map(lambda x: hex(x), expected_words))

    assert bytes32_to_words64 == expected_words_hex
    