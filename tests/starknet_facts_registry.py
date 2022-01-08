import pytest
import asyncio
from typing import NamedTuple

from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.testing.starknet import Starknet
from starkware.starkware_utils.error_handling import StarkException

from utils.types import Data
from utils.Signer import Signer
from utils.create_account import create_account
from utils.helpers import chunk_bytes_input, bytes_to_int, Encoding
from utils.block_header import build_block_header

from mocks.blocks import mocked_blocks

bytes_to_int_big = lambda word: bytes_to_int(word)

class BaseTestsDeps(NamedTuple):
    starknet: Starknet
    facts_registry: StarknetContract
    account: StarknetContract
    signer: Signer

class RegistryTestsDeps(NamedTuple):
    starknet: Starknet
    facts_registry: StarknetContract
    account: StarknetContract
    signer: Signer
    l1_relayer_account: StarknetContract
    l1_relayer_signer: Signer
    storage_proof: StarknetContract

@pytest.fixture(scope='module')
def event_loop():
    return asyncio.new_event_loop()

async def setup():
    starknet = await Starknet.empty()
    facts_registry = await starknet.deploy(source="contracts/starknet/FactsRegistry.cairo", cairo_path=["contracts"])
    account, signer = await create_account(starknet)

    return BaseTestsDeps(
        starknet=starknet,
        facts_registry=facts_registry,
        account=account,
        signer=signer)

@pytest.fixture(scope='module')
async def base_factory():
    return await setup()

@pytest.fixture(scope='module')
async def registry_initialized():
    starknet, facts_registry, account, signer = await setup()

    storage_proof = await starknet.deploy(source="contracts/starknet/L1HeadersStore.cairo", cairo_path=["contracts"])
    l1_relayer_account, l1_relayer_signer = await create_account(starknet)

    await signer.send_transaction(
        account, storage_proof.contract_address, 'initialize', [l1_relayer_account.contract_address])

    await signer.send_transaction(
        account, facts_registry.contract_address, 'initialize', [storage_proof.contract_address])

    block = mocked_blocks[2]
    block_header = build_block_header(block)
    block_rlp = block_header.raw_rlp()
    block_rlp_chunked = chunk_bytes_input(block_rlp)
    block_rlp_formatted = list(map(bytes_to_int_big, block_rlp_chunked))

    block_parent_hash = Data.from_hex("0x62a8a05ef6fcd39a11b2d642d4b7ab177056e1eb4bde4454f67285164ef8ce65")
    assert block_parent_hash.to_hex() == block_header.hash().hex()

    # Submit blockhash from L1
    await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'receive_from_l1',
        [len(block_parent_hash.to_ints(Encoding.LITTLE).values)] + block_parent_hash.to_ints(Encoding.LITTLE).values + [mocked_blocks[2]['number'] + 1])

    await l1_relayer_signer.send_transaction(
        l1_relayer_account,
        storage_proof.contract_address,
        'process_block',
        [len(block_rlp)] + [block['number']] + [len(block_rlp_formatted)] + block_rlp_formatted
    )

    return RegistryTestsDeps(
        starknet=starknet,
        facts_registry=facts_registry,
        storage_proof=storage_proof,
        account=account,
        signer=signer,
        l1_relayer_account=l1_relayer_account,
        l1_relayer_signer=l1_relayer_signer
    )


@pytest.mark.asyncio
async def test_initializer(base_factory):
    starknet, facts_registry, account, signer = base_factory

    l1_headers_store_addr = 0xbeaf

    await signer.send_transaction(
        account, facts_registry.contract_address, 'initialize', [l1_headers_store_addr])

    # Ensure address has been correctly set
    get_l1_headers_store_addr_call = await facts_registry.get_l1_headers_store_addr().call()
    set_l1_headers_store_addr = get_l1_headers_store_addr_call.result.res
    assert set_l1_headers_store_addr == l1_headers_store_addr

    # Ensure contract can't be initialized one more time
    with pytest.raises(StarkException):
        await signer.send_transaction(
            account, facts_registry.contract_address, 'initialize', [l1_headers_store_addr])


@pytest.mark.asyncio
async def test_prove_account(registry_initialized):
    starknet, facts_registry, storage_proof, account, signer, l1_relayer_account, l1_relayer_signer = registry_initialized




