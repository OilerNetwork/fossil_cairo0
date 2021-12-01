from typing import List, NamedTuple
import pytest
from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.testing.starknet import Starknet

from utils.helpers import chunk_bytes_input, bytes_to_int_big
from utils.block_header import build_block_header
from utils.benchmarks.extract_from_block_rlp import extract_from_block_rlp
from mocks.blocks import mocked_blocks


class TestsDeps(NamedTuple):
    starknet: Starknet
    decoder: StarknetContract


async def setup():
    starknet = await Starknet.empty()
    decoder = await starknet.deploy("contracts/starknet/test/TestRlpDecoder.cairo", cairo_path=["contracts"])
    return TestsDeps(starknet=starknet, decoder=decoder)


@pytest.mark.asyncio
async def test_decode_parent_hash():
    starknet, decoder = await setup()

    # Retrieve rlp block header
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()

    assert block_header.hash() == block["hash"]
    block_rlp_chunked = chunk_bytes_input(block_rlp)
    block_rlp_formatted = list(map(bytes_to_int_big, block_rlp_chunked))

    decoded = await decoder.test_decode_parent_hash(block_rlp_formatted).call()
    output = '0x' + ''.join(v.to_bytes(8, 'big').hex() for v in decoded.result.res)

    expected_words = extract_from_block_rlp(block_rlp_formatted, 32, 32 * 8)
    expected_hash = '0x' + ''.join(v.to_bytes(8, 'big').hex() for v in expected_words)

    print("Python: " ,expected_hash)
    print("Cairo: ", output)
    print("Block: ", block["parentHash"].hex())

    assert output == expected_hash
