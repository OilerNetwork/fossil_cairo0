from typing import NamedTuple
import pytest

from utils.helpers import chunk_bytes_input, bytes_to_int, ints_array_to_bytes, random_bytes

from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.testing.starknet import Starknet

class TestsDeps(NamedTuple):
    starknet: Starknet
    extract_rlp_contract: StarknetContract


bytes_to_int_big = lambda word: bytes_to_int(word)


async def setup():
    starknet = await Starknet.empty()
    extract_rlp_contract = await starknet.deploy(source="contracts/starknet/test/TestExtractFromRlp.cairo", cairo_path=["contracts"])
    return TestsDeps(
        starknet=starknet,
        extract_rlp_contract=extract_rlp_contract
    )


@pytest.mark.asyncio
async def test_random():
    starknet, extract_rlp_contract = await setup()
    block_rlp = random_bytes(1337)
    # print("\n0x" + block_rlp.hex())

    block_rlp_chunked = chunk_bytes_input(block_rlp)
    block_rlp_formatted = list(map(bytes_to_int_big, block_rlp_chunked))

    for start_byte in range(0, 20):
        for size in range(1, 35):
            extracted_words_call = await extract_rlp_contract.test_extractData(start_byte, size, block_rlp_formatted).call()
            extracted_words = extracted_words_call.result.res
            extracted_bytes = ints_array_to_bytes(extracted_words, size)
            expected_bytes = block_rlp[start_byte:start_byte+size]
            assert extracted_bytes == expected_bytes

