import pytest
from starkware.starknet.testing.starknet import Starknet


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
        int.from_bytes(b'11111111', 'little'),
        int.from_bytes(b'gabzsvmf', 'little'),
        int.from_bytes(b'eixnkgck', 'little'),
        int.from_bytes(b'llvydhra', 'little'),
        int.from_bytes(b'wqlxblbw', 'little'),
        int.from_bytes(b'aiesgdya', 'little'),
        int.from_bytes(b'onwcttdj', 'little'),
        int.from_bytes(b'elybogdy', 'little'),
        int.from_bytes(b'ruqjjeca', 'little'),
        int.from_bytes(b'xyzkbtgx', 'little'),
        int.from_bytes(b'mflkrzih', 'little'),
        int.from_bytes(b'jrmorulg', 'little'),
        int.from_bytes(b'ffzqceeb', 'little'),
        int.from_bytes(b'emlhjdhg', 'little'),
        int.from_bytes(b'zhamobne', 'little'),
        int.from_bytes(b'sgomqsy1', 'little'),
        int.from_bytes(b'22222222', 'little')
    ]

    starknet_hashed = await contract.test_keccak256(keccak_input).call()
    print(starknet_hashed)


