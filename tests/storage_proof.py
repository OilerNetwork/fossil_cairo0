import pytest
from typing import NamedTuple
from web3 import Web3

from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.testing.starknet import Starknet

from rlp import encode
from eth_utils import encode_hex
from utils.Signer import Signer
from utils.block_header import build_block_header
from utils.create_account import create_account
from utils.helpers import hexbyte_to_int, concat_arr, chunk_hex_input, string_to_byte


from mocks.blocks import mocked_blocks


class TestsDeps(NamedTuple):
    starknet: Starknet
    storage_proof: StarknetContract
    account: StarknetContract
    signer: Signer
    l1_relayer_account: StarknetContract
    l1_relayer_signer: Signer

async def setup():
    starknet = await Starknet.empty()
    storage_proof = await starknet.deploy(source="contracts/starknet/L1StorageProof.cairo", cairo_path=["contracts"])
    account, signer = await create_account(starknet)
    l1_relayer_account, l1_relayer_signer = await create_account(starknet)
    await signer.send_transaction(
        account, storage_proof.contract_address, 'initialize', [l1_relayer_account.contract_address])
    
    return TestsDeps(
        starknet=starknet,
        storage_proof=storage_proof,
        account=account,
        signer=signer,
        l1_relayer_account=l1_relayer_account,
        l1_relayer_signer=l1_relayer_signer
    )


# The path to the contract source code.


# The testing library uses python's asyncio. So the following
# decorator and the ``async`` keyword are needed.
@pytest.mark.asyncio
async def test_submit_hash():
    starknet, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = await setup()
    # Submit message using l1_relayer_account
    message = Web3.keccak(text="hello world")
    chunked_message = chunk_hex_input(message, False)

    assert len(chunked_message) == 4

    formatted_words = list(map(hexbyte_to_int, chunked_message))

    await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'submit_l1_blockhash',
        [4] + formatted_words
    )

    get_submitted_hash_call = await storage_proof.get_l1_blockhash().call()
    (word_1, word_2, word_3, word_4) = get_submitted_hash_call.result.res
    assert formatted_words[0] == word_1
    assert formatted_words[1] == word_2
    assert formatted_words[2] == word_3
    assert formatted_words[3] == word_4


@pytest.mark.asyncio
async def test_process_block():
    starknet, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = await setup()
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = encode(block_header)
    assert block_header.hash() == block["hash"]
    block_rlp_chunked = chunk_hex_input(encode_hex(block_rlp))
    block_rlp_formatted = list(map(string_to_byte, block_rlp_chunked))

    message = block["hash"]
    chunked_message = chunk_hex_input(message, False)

    formatted_words = list(map(hexbyte_to_int, chunked_message))

    await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'submit_l1_blockhash',
        [4] + formatted_words
    )

    print("About to fail")

    await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'process_block',
        [len(concat_arr(block_rlp_chunked))] + [len(block_rlp_formatted)] + block_rlp_formatted
    )








    
