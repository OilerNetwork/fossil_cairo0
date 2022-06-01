import asyncio
import pytest
from typing import NamedTuple
from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.testing.starknet import Starknet
from web3 import Web3

from utils.helpers import (
    concat_arr,
    bytes_to_int,
    chunk_bytes_input
)
from utils.block_header import build_block_header
from mocks.blocks import mocked_blocks


class TestsDeps(NamedTuple):
    starknet: Starknet
    keccak_contract: StarknetContract

@pytest.fixture(scope='module')
def event_loop():
    return asyncio.new_event_loop()

async def setup():
    starknet = await Starknet.empty()
    keccak_contract = await starknet.deploy(source="contracts/starknet/test/TestKeccak256.cairo", cairo_path=["contracts"])
    return TestsDeps(
        starknet=starknet,
        keccak_contract=keccak_contract
    )

@pytest.fixture(scope='module')
async def factory():
    return await setup()


bytes_to_int_big = lambda word: bytes_to_int(word)


# The testing library uses python's asyncio. So the following
# decorator and the ``async`` keyword are needed.
@pytest.mark.asyncio
async def test_small_input(factory):
    starknet, keccak_contract = factory

    keccak_input = [
        b'\xf9\x02\x18\xa0\x03\xb0\x16\xcc',
        b'\x93\x87\xcb\x3c\xef\x86\xd9\xd4',
        b'\xaf\xb5\x2c\x37\x89\x52\x8c\x53',
        b'\x0c\x00\x20\x87\x95\xac\x93\x7c',
        b'\x00\x00\x00\x00\x00\x00\x00\x77',
    ]
    
    web3_computed_hash = Web3.keccak(concat_arr(keccak_input)).hex()

    test_keccak_call = await keccak_contract.test_keccak256(
        len(concat_arr(keccak_input)), list(map(bytes_to_int_big, keccak_input))
    ).call()

    print(test_keccak_call)

    starknet_hashed = test_keccak_call.result.res
    output = '0x' + ''.join(v.to_bytes(8, 'big').hex() for v in starknet_hashed)

    assert output == web3_computed_hash


@pytest.mark.asyncio
async def test_small_tricky_input(factory):
    starknet, keccak_contract = factory

    keccak_input = [
        b'\xf9\x02\x18\xa0\x03\xb0\x16\xcc',
        b'\x93\x87\xcb\x3c\xef\x86\xd9\xd4',
        b'\xaf\xb5\x2c\x37\x89\x52\x8c\x53',
        b'\x0c\x00\x20\x87\x95\xac\x93\x7c',
        b'\x00\x77',
    ]
    
    web3_computed_hash = Web3.keccak(concat_arr(keccak_input)).hex()

    test_keccak_call = await keccak_contract.test_keccak256(
        len(concat_arr(keccak_input)), list(map(bytes_to_int_big, keccak_input))
    ).call()


    starknet_hashed = test_keccak_call.result.res
    output = '0x' + ''.join(v.to_bytes(8, 'big').hex() for v in starknet_hashed)

    assert output == web3_computed_hash


@pytest.mark.asyncio
async def test_huge_input(factory):
    starknet, keccak_contract = factory

    keccak_input = [
        b'\xf9\x02\x18\xa0\x03\xb0\x16\xcc',
        b'\x93\x87\xcb\x3c\xef\x86\xd9\xd4',
        b'\xaf\xb5\x2c\x37\x89\x52\x8c\x53',
        b'\x0c\x00\x20\x87\x95\xac\x93\x7c',
        b'\xe0\x45\x59\x6a\xa0\x1d\xcc\x4d',
        b'\xe8\xde\xc7\x5d\x7a\xab\x85\xb5',
        b'\x67\xb6\xcc\xd4\x1a\xd3\x12\x45',
        b'\x1b\x94\x8a\x74\x13\xf0\xa1\x42',
        b'\xfd\x40\xd4\x93\x47\x94\xfb\xb6',
        b'\x1b\x8b\x98\xa5\x9f\xbc\x4b\xd7',
        b'\x9c\x23\x21\x2a\xdd\xbe\xfa\xeb',
        b'\x28\x9f\xa0\xd4\x5c\xea\x1d\x5c',
        b'\xae\x78\x38\x6f\x79\xe0\xd5\x22',
        b'\xe0\xa1\xd9\x1b\x2d\xa9\x5f\xf8',
        b'\x4b\x5d\xe2\x58\xf2\xc9\x89\x3d',
        b'\x3f\x49\xb1\xa0\x14\x07\x4f\x25',
        b'\x3a\x03\x23\x23\x1d\x34\x9a\x3f',
        b'\x9c\x64\x6a\xf7\x71\xc1\xde\xc2',
        b'\xf2\x34\xbb\x80\xaf\xed\x54\x60',
        b'\xf5\x72\xfe\xd1\xa0\x5a\x6f\x5b',
        b'\x9a\xc7\x5a\xe1\xe1\xf8\xc4\xaf',
        b'\xef\xb9\x34\x7e\x14\x1b\xc5\xc9',
        b'\x55\xb2\xed\x65\x34\x1d\xf3\xe1',
        b'\xd5\x99\xfc\xad\x91\xb9\x01\x00',
        b'\x00\x00\x00\x00\x00\x00\x00\x00',
        b'\x00\x00\x00\x00\x00\x00\x00\x00',
        b'\x00\x00\x00\x00\x00\x00\x00\x00',
        b'\x00\x00\x00\x00\x00\x00\x00\x00',
        b'\x00\x00\x00\x00\x00\x00\x00\x00',
        b'\x00\x00\x00\x00\x00\x00\x00\x00',
        b'\x00\x00\x00\x00\x00\x00\x00\x00',
        b'\x00\x00\x00\x00\x00\x00\x00\x00',
        b'\x00\x00\x00\x00\x00\x00\x00\x00',
        b'\x00\x00\x00\x00\x00\x00\x00\x00',
        b'\x00\x00\x00\x00\x00\x00\x00\x00',
        b'\x00\x00\x00\x00\x00\x00\x00\x00',
        b'\x00\x00\x00\x00\x00\x00\x00\x00',
        b'\x00\x00\x00\x00\x00\x00\x00\x00',
        b'\x00\x00\x00\x00\x00\x00\x00\x00',
        b'\x00\x00\x00\x00\x00\x00\x00\x00',
        b'\x00\x00\x00\x00\x00\x00\x00\x00',
        b'\x00\x00\x00\x00\x00\x00\x00\x00',
        b'\x00\x00\x00\x00\x00\x00\x00\x00',
        b'\x00\x00\x00\x00\x00\x00\x00\x00',
        b'\x00\x00\x00\x00\x00\x00\x00\x00',
        b'\x00\x00\x00\x00\x00\x00\x00\x00',
        b'\x00\x00\x00\x00\x00\x00\x00\x00',
        b'\x00\x00\x00\x00\x00\x00\x00\x00',
        b'\x00\x00\x00\x00\x00\x00\x00\x00',
        b'\x00\x00\x00\x00\x00\x00\x00\x00',
        b'\x00\x00\x00\x00\x00\x00\x00\x00',
        b'\x00\x00\x00\x00\x00\x00\x00\x00',
        b'\x00\x00\x00\x00\x00\x00\x00\x00',
        b'\x00\x00\x00\x00\x00\x00\x00\x00',
        b'\x00\x00\x00\x00\x00\x00\x00\x00',
        b'\x00\x00\x00\x00\x00\x00\x00\x00',
        b'\x84\x76\xfe\x29\x0a\x83\xae\xce',
        b'\x98\x83\x7a\x12\x00\x83\x17\xed',
        b'\xcf\x84\x61\x97\xc0\x24\x99\xd8',
        b'\x83\x01\x0a\x0c\x84\x67\x65\x74',
        b'\x68\x88\x67\x6f\x31\x2e\x31\x37',
        b'\x2e\x31\x85\x6c\x69\x6e\x75\x78',
        b'\xa0\x73\x2d\x0e\xad\x04\x88\x3a',
        b'\x10\x97\x64\x63\xe5\xd4\xf7\x14',
        b'\xc0\xb2\xa8\x1a\x74\x61\x34\xe9',
        b'\xc2\x34\x1f\x59\xb6\xc7\x61\x0c',
        b'\x03\x88\x3f\x40\xad\x5a\x09\xe2',
        b'\xd5\x00\x18',
    ]

    web3_computed_hash = Web3.keccak(concat_arr(keccak_input)).hex()

    test_keccak_call = await keccak_contract.test_keccak256(
        len(concat_arr(keccak_input)), list(map(bytes_to_int_big, keccak_input))
    ).call()

    starknet_hashed = test_keccak_call.result.res
    output = '0x' + ''.join(v.to_bytes(8, 'big').hex() for v in starknet_hashed)

    assert output == web3_computed_hash


@pytest.mark.asyncio
async def test_blockheader_input(factory):
    starknet, keccak_contract = factory

    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()

    assert block_header.hash() == block["hash"]
    block_rlp_chunked = chunk_bytes_input(block_rlp)

    test_keccak_call_big = await keccak_contract.test_keccak256(
        len(block_rlp),
        list(map(bytes_to_int_big, block_rlp_chunked))
    ).call()
    starknet_hashed_big = test_keccak_call_big.result.res

    print(test_keccak_call_big)

    output = '0x' + ''.join(v.to_bytes(8, 'big').hex() for v in starknet_hashed_big)
    assert output == block["hash"].hex()

