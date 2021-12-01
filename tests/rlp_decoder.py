from typing import List, NamedTuple
import pytest
from starkware.starknet.testing.contract import StarknetContract
from utils.block_header import build_block_header
from mocks.blocks import mocked_blocks
from utils.helpers import chunk_bytes_input, bytes_to_int_big, print_bytes_array, print_ints_array, ints_array_to_bytes
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

def decode_value_from_rlp(block_rlp_formatted: List[int], pos: int, size: int) -> str:
    start_word, start_pos = divmod(pos, 8)
    print("start_word:", start_word)
    print("start_pos:", start_pos)
    end_word, end_pos = divmod(pos+size-1, 8)
    print("end_word:", end_word)
    print("end_pos:", end_pos)
    
    shift = start_pos
    size_in_words, remainder = divmod(size, 8)

    print("size_in_words:", size_in_words)
    print("remainder:", remainder)

    words: List[int] = []

    for i in range(start_word, end_word+1):
        words.append(block_rlp_formatted[i])

    print(print_ints_array(words))

    # If only one and only word - we just crop needed part from it
    if (end_word == start_word):
        print('here 1')
        # Shift right (cropping out right not-needed part)
        words[0] = words[0] >> (8*(7-end_pos))
        # Mask is the size: (end_pos - start_pos + 1) = aka size
        mask = 2**(8*(end_pos - start_pos + 1)) - 1
        # We apply the mask to leave just the needed part on the right (size bytes)
        words[0] = words[0] & mask
    else:
        # If two words
        if (end_word == start_word + 1):
            print('here 2')
            # If no shifting is needed - we just cut the second word
            if (shift == 0):
                # Shift right (cropping out right not-needed part)
                words[1] = words[1] >> (8*(7-end_pos))
                # Mask is the size of the remainder+1 (end_pos + 1)
                mask = 2 ** (8 * (end_pos + 1)) - 1
                # We apply the mask to leave just the needed part on the right
                words[1] = words[1] & mask
            # If there's a shift - we combine first and word with cutting both
            else:
                print('here 3')
                # TODO: This will not work if we cut just the end of first word, and beginning of second
                # Shift first word to the left, cutting not-needed bytes from the left
                words[0] = (words[0] << (8 * start_pos))                
                # Shift the second word right, cutting not-needed bytes from the right
                shifted_right_word = words[1] >> (8 * (8 - start_pos))
                # TODO: From here - it goes all wrong...
                words[0] = words[0] + shifted_right_word
                mask = (2**64 - 1)
                words[0] = words[0] & mask
        # If many words
        else:
            print('here 4')
            # If no shift is needed - we just leave all words as the are except the last one - we cut last one
            if (shift == 0):
                print('here 4:1')
                lastword_i = len(words)-1
                mask = 2 ** (8 * (end_pos + 1)) - 1
                words[lastword_i] = words[lastword_i] >> (8*(7-end_pos))
                words[lastword_i] = words[lastword_i] & mask
            # If there's shift - we repeatedly cut all words
            else:
                print('here 4:2')
                print('start_pos: ', start_pos)
                for i in range(len(words) - 1):
                    words[i] = (words[i] << (8 * start_pos)) & (2**64 - 1)
                    words[i] = words[i] + (words[i+1] >> (8 * (8 - start_pos)))
                    # TODO: I guess there might be a situation that we need to mask the last word?
    
    return words[0:size_in_words]

def decode_parent_hash(block_rlp_formatted: List[int]) -> str:
    word_0_bin = bin(block_rlp_formatted[0])[2:]

    print(word_0_bin[0:16])
    print(int(word_0_bin[0:16], 2))

    print(bin(block_rlp_formatted[0])[2:])

    word_1_bitwised = (block_rlp_formatted[0] << 32) & 2**64-1
    word_2_bitwised = block_rlp_formatted[1]
    word_3_bitwised = block_rlp_formatted[2]
    word_4_bitwised = (block_rlp_formatted[3] >> 32)

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
    output = '0x' + ''.join(v.to_bytes(8, 'big').hex() for v in decoded.result.res)

    print("Cairo output: ", output)
    print("Python output: ", decode_parent_hash(block_rlp_formatted))
    print("Expected output: ", block_header.parentHash.hex())

    message = bytearray.fromhex(block["hash"].hex()[2:])
    chunked_message = chunk_bytes_input(message)
    formatted_words = list(map(bytes_to_int_big, chunked_message))

    print("Expected hash int words representation: ", formatted_words)


# @pytest.mark.asyncio
# async def test_decode_parent_hash():
#     starknet, decoder = await setup()

#     # Retrieve rlp block header
#     block = mocked_blocks[0]
#     block_header = build_block_header(block)
#     block_rlp = block_header.raw_rlp()
#     print("\n\nBlock rlp:", block_rlp.hex())

#     assert block_header.hash() == block["hash"]

#     block_rlp_chunked = chunk_bytes_input(block_rlp)
#     block_rlp_formatted = list(map(bytes_to_int_big, block_rlp_chunked))

#     print(block_rlp_formatted)

#     print("Decoded:" ,decode_parent_hash(block_rlp_formatted))
#     print(block["parentHash"].hex()[2:])

#     result = decode_value_from_rlp(block_rlp_formatted, 4, 32)
#     # result_bytes = ints_array_to_bytes(result)

#     assert 1 == 2

#     # print(result_bytes.hex())
#     print(block["parentHash"].hex()[2:])

#     print("Parent Hash: ", decode_parent_hash(block_rlp_formatted))


#     # assert result_bytes == block["parentHash"]
