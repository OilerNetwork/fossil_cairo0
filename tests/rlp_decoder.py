from typing import List, NamedTuple
import pytest
from starkware.starknet.testing.contract import StarknetContract
from utils.block_header import build_block_header
from mocks.blocks import mocked_blocks
from utils.helpers import chunk_bytes_input, bytes_to_int_big
from starkware.starknet.testing.starknet import Starknet


class TestsDeps(NamedTuple):
    starknet: Starknet
    decoder: StarknetContract


async def setup():
    starknet = await Starknet.empty()
    decoder = await starknet.deploy("contracts/starknet/test/TestRlpDecoder.cairo", cairo_path=["contracts"])
    return TestsDeps(starknet=starknet, decoder=decoder)


# @pytest.mark.asyncio
# async def test_decode_rlp():
#     starknet, decoder = await setup()

#     # Retrieve rlp block header
#     block = mocked_blocks[0]
#     block_header = build_block_header(block)
#     block_rlp = block_header.raw_rlp()

#     assert block_header.hash() == block["hash"]
#     block_rlp_chunked = chunk_bytes_input(block_rlp)
#     block_rlp_formatted = list(map(bytes_to_int, block_rlp_chunked))

#     decoded = await decoder.extract_from_rlp(block_rlp_formatted).call()
#     (block_number, parent_hash, state_root, receipts_root) = decoded.result

#     print("Decoded result: ", decoded.result)
#     print("block_header: ", block_header)
#     print("Formatted rlp: ", block_rlp_formatted)
#     print("Chunked rlp: ", block_rlp_chunked)

#     print('Block header len: ', len(block_rlp))

#     assert block_number > 0
#     assert parent_hash > 0
#     assert state_root > 0
#     assert receipts_root > 0


def decode_parent_hash(block_rlp_formatted: List[int]) -> str:
    word_0_bin = bin(block_rlp_formatted[0])[2:]

    print(word_0_bin[0:16])
    print(int(word_0_bin[0:16], 2))

    print(bin(block_rlp_formatted[0])[2:])

    word_1_bitwised = block_rlp_formatted[0] << 16
    word_2_bitwised = block_rlp_formatted[1] >> 48
    word_3_bitwised = block_rlp_formatted[2] >> 48
    word_4_bitwised = block_rlp_formatted[3] << 16

    print("Word 1: ", word_1_bitwised)
    print("Word 2: ", word_2_bitwised)
    print("Word 3: ", word_3_bitwised)
    print("Word 4: ", word_4_bitwised)


    return '0x' + ''.join(v.to_bytes(8, 'little').hex() for v in [word_1_bitwised, word_2_bitwised, word_3_bitwised, word_4_bitwised])


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

    print("Block rlp formatted: ", block_rlp_formatted)

    decoded = await decoder.test_decode_parent_hash(block_rlp_formatted).call()
    output = '0x' + ''.join(v.to_bytes(8, 'little').hex() for v in decoded.result.res)

    print("Cairo output: ", output)
    print("Python output: ", decode_parent_hash(block_rlp_formatted))
    print("Expected output: ", block_header.parentHash.hex())

    message = bytearray.fromhex(block["hash"].hex()[2:])
    chunked_message = chunk_bytes_input(message)
    formatted_words = list(map(bytes_to_int_big, chunked_message))

    print("Expected hash int words representation: ", formatted_words)




