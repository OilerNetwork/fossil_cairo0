import pytest
import asyncio

from typing import NamedTuple

from starkware.starkware_utils.error_handling import StarkException
from starkware.starknet.testing.starknet import Starknet
from starkware.starknet.testing.contract import StarknetContract

from utils.types import Data
from utils.Signer import Signer
from utils.create_account import create_account

from mocks.blocks import mocked_blocks


class TestsDeps(NamedTuple):
    starknet: Starknet
    twap: StarknetContract
    account: StarknetContract
    signer: Signer
    l1_relayer_account: StarknetContract
    l1_relayer_signer: Signer
    storage_proof: StarknetContract

@pytest.fixture(scope='module')
def event_loop():
    return asyncio.new_event_loop()

async def submit_l1_parent_hash(l1_relayer_signer: Signer, l1_relayer_account: StarknetContract, storage_proof: StarknetContract, message = mocked_blocks[0]["parentHash"].hex(), block_number = mocked_blocks[0]['number']):
    message = Data.from_hex(message).to_ints()

    await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'receive_from_l1',
        [4] + message.values + [block_number]
    )

async def setup():
    starknet = await Starknet.empty()
    account, signer = await create_account(starknet)
    l1_relayer_account, l1_relayer_signer = await create_account(starknet)
    twap = await starknet.deploy(source="contracts/starknet/TWAP.cairo", cairo_path=["contracts"])
    storage_proof = await starknet.deploy(source="contracts/starknet/L1HeadersStore.cairo", cairo_path=["contracts"])

    await signer.send_transaction(
        account, storage_proof.contract_address, 'initialize', [l1_relayer_account.contract_address])

    await signer.send_transaction(
        account, twap.contract_address, 'initialize', [storage_proof.contract_address])

    await submit_l1_parent_hash(l1_relayer_signer, l1_relayer_account, storage_proof, mocked_blocks[0]['hash'].hex()[2:], mocked_blocks[0]['number'] + 1)

    return TestsDeps(
        starknet=starknet,
        twap=twap,
        account=account,
        signer=signer,
        l1_relayer_account=l1_relayer_account,
        l1_relayer_signer=l1_relayer_signer,
        storage_proof=storage_proof)

@pytest.fixture(scope='module')
async def factory():
    return await setup()

@pytest.mark.asyncio
async def test_initializer(factory):
    starknet, twap, account, signer, l1_relayer_account, l1_relayer_signer, storage_proof = factory
    pass

@pytest.mark.asyncio
async def test_register_computation(factory):
    starknet, twap, account, signer, l1_relayer_account, l1_relayer_signer, storage_proof = factory
    
    await signer.send_transaction(
        account,
        twap.contract_address,
        'register_computation',
        [mocked_blocks[0]['number'], 2, 3, 4]
    )
