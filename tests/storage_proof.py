import pytest
from typing import NamedTuple

from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.testing.starknet import Starknet

from utils.Signer import Signer
from utils.block_header import build_block_header
from utils.create_account import create_account
from utils.helpers import chunk_bytes_input, bytes_to_int_big, bytes_to_int_little


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
    
    block = mocked_blocks[0]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()
    assert block_header.hash() == block["hash"]
    block_rlp_chunked = chunk_bytes_input(block_rlp)

    message = bytearray.fromhex(block["hash"].hex()[2:])
    chunked_message = chunk_bytes_input(message)
    formatted_words = list(map(bytes_to_int_little, chunked_message))

    await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'submit_l1_blockhash',
        [len(formatted_words)] + formatted_words
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
    block_rlp = block_header.raw_rlp()
    assert block_header.hash() == block["hash"]
    block_rlp_chunked = chunk_bytes_input(block_rlp)
    block_rlp_formatted = list(map(bytes_to_int_big, block_rlp_chunked))

    message = bytearray.fromhex(block["hash"].hex()[2:])
    chunked_message = chunk_bytes_input(message)
    formatted_words = list(map(bytes_to_int_little, chunked_message))

    await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'submit_l1_blockhash',
        [len(formatted_words)] + formatted_words
    )

    get_submitted_hash_call = await storage_proof.get_l1_blockhash().call()
    set_hash_words = get_submitted_hash_call.result.res

    keccak_contract = await starknet.deploy(source="contracts/starknet/test/TestKeccak256.cairo", cairo_path=["contracts"])
    test_keccak_call = await keccak_contract.test_keccak256(
        len(block_rlp),
        block_rlp_formatted
    ).call()
    starknet_hashed_words = test_keccak_call.result.res

    for i in range(0, 3):
        assert list(set_hash_words)[i] == list(starknet_hashed_words)[i]

    await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'process_block',
        [len(block_rlp)] + [len(block_rlp_formatted)] + block_rlp_formatted
    )








    
