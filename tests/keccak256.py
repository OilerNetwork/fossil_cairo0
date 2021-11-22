from typing import NamedTuple
import pytest
from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.testing.starknet import Starknet
from web3 import Web3

from rlp import encode
from eth_utils import encode_hex

from utils.helpers import (
    concat_arr,
    string_to_byte,
    bytes_to_int,
    chunk_hex_input,
    hex_string_to_byte,
    chunk_bytes_input
)
from utils.block_header import build_block_header
from mocks.blocks import mocked_blocks


class TestsDeps(NamedTuple):
    starknet: Starknet
    keccak_contract: StarknetContract


async def setup():
    starknet = await Starknet.empty()
    keccak_contract = await starknet.deploy(source="contracts/starknet/test/TestKeccak256.cairo", cairo_path=["contracts"])
    return TestsDeps(
        starknet=starknet,
        keccak_contract=keccak_contract
    )



# The testing library uses python's asyncio. So the following
# decorator and the ``async`` keyword are needed.
@pytest.mark.asyncio
async def test_keccak256():
    starknet, keccak_contract = await setup()

    keccak_input = [
        'f90218a0',
        '03b016cc',
        '9387cb3c',
        'ef86d9d4',
        'afb52c37',
        '89528c53',
        '0c002087',
        '95ac937c',
        'e045596a',
        'a01dcc4d',
        'e8dec75d',
        '7aab85b5',
        '67b6ccd4',
        '1ad31245',
        '1b948a74',
        '13f0a142',
        'fd40d493',
        '4794fbb6',
        '1b8b98a5',
        '9fbc4bd7',
        '9c23212a',
        'ddbefaeb',
        '289fa0d4',
        '5cea1d5c',
        'ae78386f',
        '79e0d522',
        'e0a1d91b',
        '2da95ff8',
        '4b5de258',
        'f2c9893d',
        '3f49b1a0',
        '14074f25',
        '3a032323',
        '1d349a3f',
        '9c646af7',
        '71c1dec2',
        'f234bb80',
        'afed5460',
        'f572fed1',
        'a05a6f5b',
        '9ac75ae1',
        'e1f8c4af',
        'efb9347e',
        '141bc5c9',
        '55b2ed65',
        '341df3e1',
        'd599fcad',
        '91b90100',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '00000000',
        '8476fe29',
        '0a83aece',
        '98837a12',
        '008317ed',
        'cf846197',
        'c02499d8',
        '83010a0c',
        '84676574',
        '6888676f',
        '312e3137',
        '2e31856c',
        '696e7578',
        'a0732d0e',
        'ad04883a',
        '10976463',
        'e5d4f714',
        'c0b2a81a',
        '746134e9',
        'c2341f59',
        'b6c7610c',
        '03883f40',
        'ad5a09e2',
        'd50018'
    ]
    
    web3_computed_hash = Web3.keccak(concat_arr(keccak_input).encode('UTF-8', 'little')).hex()

    test_keccak_call = await keccak_contract.test_keccak256(
        len(concat_arr(keccak_input)), list(map(string_to_byte, keccak_input))
    ).call()


    starknet_hashed = test_keccak_call.result.res
    output = '0x' + ''.join(v.to_bytes(8, 'little').hex() for v in starknet_hashed)

    assert output == web3_computed_hash


@pytest.mark.asyncio
async def test_blockhash_hashing():
    starknet, keccak_contract = await setup()

    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()

    assert block_header.hash() == block["hash"]
    block_rlp_chunked = chunk_bytes_input(block_rlp)
    block_rlp_formatted = list(map(bytes_to_int, block_rlp_chunked))

    test_keccak_call = await keccak_contract.test_keccak256(
        len(block_rlp),
        block_rlp_formatted
    ).call()

    starknet_hashed = test_keccak_call.result.res
    output = '0x' + ''.join(v.to_bytes(8, 'little').hex() for v in starknet_hashed)

    assert output == block["hash"].hex()

