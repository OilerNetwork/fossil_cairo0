import asyncio
import pytest
from typing import NamedTuple
from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.testing.starknet import Starknet
from web3 import Web3

from utils.helpers import (concat_arr, bytes_to_int, chunk_bytes_input)

from utils.block_header import build_block_header
from mocks.blocks import mocked_blocks

from utils.types import Data

bytes_to_int_big = lambda word: bytes_to_int(word)

class TestsDeps(NamedTuple):
    starknet: Starknet
    keccak_contract: StarknetContract

@pytest.fixture(scope='module')
def event_loop():
    return asyncio.new_event_loop()

async def setup():
    starknet = await Starknet.empty()
    keccak_contract = await starknet.deploy(source="contracts/starknet/test/TestUnsafeKeccak256.cairo", cairo_path=["contracts"])
    return TestsDeps(
        starknet=starknet,
        keccak_contract=keccak_contract
    )

@pytest.fixture(scope='module')
async def factory():
    return await setup()

@pytest.mark.asyncio
async def test_against_web3(factory):
    starknet, keccak_contract = factory

    keccak_input = [
        b'\xf9\x02\x18\xa0\x03\xb0\x16\xcc',
        b'\x93\x87\xcb\x3c\xef\x86\xd9\xd4',
        b'\xaf\xb5\x2c\x37\x89\x52\x8c\x53',
        b'\x0c\x00\x20\x87\x95\xac\x93\x7c',
        b'\x00\x00\x00\x00\x00\x00\x00\x77',
    ]
    
    web3_computed_hash = Web3.keccak(concat_arr(keccak_input)).hex()

    test_keccak_call = await keccak_contract.test_unsafe_keccak256(
        len(concat_arr(keccak_input)), list(map(bytes_to_int_big, keccak_input))
    ).call()

    starknet_hashed = test_keccak_call.result.res
    output = '0x' + ''.join(v.to_bytes(8, 'big').hex() for v in starknet_hashed)

    assert output == web3_computed_hash

@pytest.mark.asyncio
async def test_hash_header(factory):
    starknet, keccak_contract = factory

    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()

    block_rlp_chunked = Data.from_bytes(block_rlp).to_ints()

    assert block_header.hash() == block["hash"]

    test_keccak_call_big = await keccak_contract.test_unsafe_keccak256(
        block_rlp_chunked.length,
        block_rlp_chunked.values
    ).call()
    starknet_hashed_big = test_keccak_call_big.result.res

    print("Number of steps: ", test_keccak_call_big.call_info.execution_resources.n_steps)

    output = '0x' + ''.join(v.to_bytes(8, 'big').hex() for v in starknet_hashed_big)
    assert output == block["hash"].hex()

@pytest.mark.asyncio
async def test_against_safe_implementation(factory):
    starknet, unsafe_keccak_contract = factory
    safe_keccak_contract = await starknet.deploy(source="contracts/starknet/test/TestKeccak256.cairo", cairo_path=["contracts"])

    keccak_input = [
        b'\xf9\x02\x18\xa0\x03\xb0\x16\xcc',
        b'\x93\x87\xcb\x3c\xef\x86\xd9\xd4',
        b'\xaf\xb5\x2c\x37\x89\x52\x8c\x53',
        b'\x0c\x00\x20\x87\x95\xac\x93\x7c',
        b'\x00\x00\x00\x00\x00\x00\x00\x77',
    ]

    safe_keccak_call = await safe_keccak_contract.test_keccak256(
        len(concat_arr(keccak_input)), list(map(bytes_to_int_big, keccak_input))
    ).call()
    safe_keccak_output = '0x' + ''.join(v.to_bytes(8, 'big').hex() for v in safe_keccak_call.result.res)
    
    test_unsafe_keccak_call = await unsafe_keccak_contract.test_unsafe_keccak256(
        len(concat_arr(keccak_input)), list(map(bytes_to_int_big, keccak_input))
    ).call()
    unsafe_keccak_output = '0x' + ''.join(v.to_bytes(8, 'big').hex() for v in test_unsafe_keccak_call.result.res)

    assert unsafe_keccak_output == safe_keccak_output