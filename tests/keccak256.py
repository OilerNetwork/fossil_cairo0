import pytest
from starkware.starknet.testing.starknet import Starknet
from web3 import Web3
import functools
from typing import Callable, List


# The testing library uses python's asyncio. So the following
# decorator and the ``async`` keyword are needed.
@pytest.mark.asyncio
async def test_keccak256():
    # Create a new Starknet class that simulates the StarkNet
    # system.
    starknet = await Starknet.empty()

    # Deploy the contract.
    contract = await starknet.deploy(source="contracts/starknet/test/TestKeccak256.cairo", cairo_path=["contracts"])

    keccak_input = [
        '11111111',
        'gabzsvmf',
        'eixnkgck',
        'llvydhra',
        'wqlxblbw',
        'aiesgdya',
        'onwcttdj',
        'elybogdy',
        'ruqjjeca',
        'xyzkbtgx',
        'mflkrzih',
        'jrmorulg',
        'ffzqceeb',
        'emlhjdhg',
        'zhamobne',
        'sgomqsy1',
        '22222222',
        '33333333',
        'gabzsvmf',
        'eixnkgck',
        'llvydhra',
        'wqlxblbw',
        'aiesgdya',
        'onwcttdj',
        'elybogdy',
        'ruqjjeca',
        'xyzkbtgx',
        'mflkrzih',
        'jrmorulg',
        'ffzqceeb',
        'emlhjdhg',
        'zhamobne',
        'sgomqsy1',
        "sgoma"
    ]
    
    concat_arr: Callable[[List[str]], str] = lambda arr: functools.reduce(lambda a, b: a + b, arr)
    web3_computed_hash = Web3.keccak(text=concat_arr(keccak_input)).hex()

    string_to_byte: Callable[[str], int] = lambda word: int.from_bytes(word.encode("UTF-8"), 'little')

    test_keccak_call = await contract.test_keccak256(
        len(concat_arr(keccak_input)),
        list(map(string_to_byte, keccak_input))
    ).call()


    starknet_hashed = test_keccak_call.result.res
    output = '0x' + ''.join(v.to_bytes(8, 'little').hex() for v in starknet_hashed)

    assert output == web3_computed_hash



