import pytest
from web3 import Web3
from rlp import encode
from eth_utils import encode_hex
from utils.block_header import build_block_header
from starkware.starknet.testing.starknet import Starknet


config = {
    "JSON_RPC_PROVIDER_URL": "https://eth-ropsten.alchemyapi.io/v2/sgu74vE7DFD1ePkfwC9SW0lCeFDC3K6o"
}


# The testing library uses python's asyncio. So the following
# decorator and the ``async`` keyword are needed.
@pytest.mark.asyncio
async def test_decode_rlp():
    # Create a new Starknet class that simulates the StarkNet
    # system.
    starknet = await Starknet.empty()

    # Deploy the contract.
    decoder = await starknet.deploy("contracts/starknet/test/TestRlpDecoder.cairo")


    # Retrieve rlp block header
    http_provider = Web3.HTTPProvider(config['JSON_RPC_PROVIDER_URL'])
    web3 = Web3(http_provider)
    block = web3.eth.get_block('latest')
    block_header = build_block_header(block)
    block_rlp = encode(block_header)
    assert block_header.hash() == block["hash"]
    block_rlp_chunked = [encode_hex(block_rlp)[i+0:i+8] for i in range(2, len(block_rlp), 8)]
    block_rlp_formatted = list(map(lambda word: int.from_bytes(word.encode("UTF-8"), 'little'), block_rlp_chunked))


    decoded = await decoder.extract_from_rlp(block_rlp_formatted).call()
    (block_number, parent_hash, state_root, receipts_root) = decoded.result
    print(block_number, parent_hash, state_root, receipts_root)




