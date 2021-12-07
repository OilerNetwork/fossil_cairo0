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


# @pytest.mark.asyncio
# async def test_submit_hash():
#     starknet, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = await setup()
#     # Submit message using l1_relayer_account
    
#     block = mocked_blocks[0]
#     block_header = build_block_header(block)
#     block_rlp = block_header.raw_rlp()
#     assert block_header.hash() == block["hash"]
#     block_rlp_chunked = chunk_bytes_input(block_rlp)

#     message = bytearray.fromhex(block["hash"].hex()[2:])
#     chunked_message = chunk_bytes_input(message)
#     formatted_words = list(map(bytes_to_int_little, chunked_message))

#     await l1_relayer_signer.send_transaction(
#         l1_relayer_account,
#         storage_proof.contract_address,
#         'receive_from_l1',
#         [len(formatted_words)] + formatted_words + [block['number']]
#     )


@pytest.mark.asyncio
async def test_process_block():
    starknet, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = await setup()

    block = mocked_blocks[1]
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
        'receive_from_l1',
        [len(formatted_words)] + formatted_words + [mocked_blocks[0]['number']]
    )

    await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'process_block',
        [block['number']] + [len(block_rlp)] + [len(block_rlp_formatted)] + block_rlp_formatted
    )








    
