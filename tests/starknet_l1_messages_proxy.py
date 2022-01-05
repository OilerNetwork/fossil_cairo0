import pytest

from typing import NamedTuple

from starkware.starkware_utils.error_handling import StarkException
from starkware.starknet.testing.starknet import Starknet
from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.compiler.compile import get_selector_from_name

from utils.Signer import Signer

from utils.create_account import create_account
from utils.helpers import chunk_bytes_input, bytes_to_int_little

from mocks.blocks import mocked_blocks


class TestsDeps(NamedTuple):
    starknet: Starknet
    messages_proxy: StarknetContract
    account: StarknetContract
    signer: Signer

async def setup():
    starknet = await Starknet.empty()
    messages_proxy = await starknet.deploy(source="contracts/starknet/L1MessagesProxy.cairo", cairo_path=["contracts"])
    account, signer = await create_account(starknet)

    return TestsDeps(
       starknet=starknet,
       messages_proxy=messages_proxy,
       account=account,
       signer=signer)

@pytest.mark.asyncio
async def test_receive_from_l1():
    starknet, messages_proxy, account, signer = await setup()

    l1_headers_store = await starknet.deploy(source="contracts/starknet/L1HeadersStore.cairo", cairo_path=["contracts"])

    l1_messages_sender = 0xbeaf
    l1_headers_store_addr = l1_headers_store.contract_address
    owner = account.contract_address
    await signer.send_transaction(
        account, messages_proxy.contract_address, 'initialize', [l1_messages_sender, l1_headers_store_addr, owner])
    
    message = bytearray.fromhex(mocked_blocks[0]["parentHash"].hex()[2:])
    chunked_message = chunk_bytes_input(message)
    formatted_words = list(map(bytes_to_int_little, chunked_message))

    # Initialize l1 headers store contract
    await signer.send_transaction(
        account, l1_headers_store.contract_address, 'initialize', [messages_proxy.contract_address])
    
    # send message to l2
    await starknet.send_message_to_l2(
        l1_messages_sender,
        messages_proxy.contract_address,
        get_selector_from_name('receive_from_l1'),
        formatted_words + [mocked_blocks[0]["number"]])
    
    parent_hash_call = await l1_headers_store.get_parent_hash(mocked_blocks[0]["number"]).call()
    set_parent_hash = '0x' + ''.join(v.to_bytes(8, 'little').hex() for v in parent_hash_call.result.res)

    assert set_parent_hash == mocked_blocks[0]["parentHash"].hex()

@pytest.mark.asyncio
async def test_change_contract_addresses():
    starknet, messages_proxy, account, signer = await setup()

    l1_messages_sender = 0xbeaf
    l1_headers_store_addr = 0xdead
    owner = account.contract_address
    await signer.send_transaction(
        account, messages_proxy.contract_address, 'initialize', [l1_messages_sender, l1_headers_store_addr, owner])
    
    new_l1_messages_sender = 0xdada
    new_l1_headers_store_addr = 0xfefe
    await signer.send_transaction(
        account, messages_proxy.contract_address, 'change_contract_addresses', [new_l1_messages_sender, new_l1_headers_store_addr])
    
    set_l1_messages_sender_call = await messages_proxy.get_l1_messages_sender().call()
    assert set_l1_messages_sender_call.result.res == new_l1_messages_sender

    set_l1_headers_store_addr_call = await messages_proxy.get_l1_headers_store_addr().call()
    assert set_l1_headers_store_addr_call.result.res == new_l1_headers_store_addr


@pytest.mark.asyncio
async def test_change_owner_invalid_caller():
    starknet, messages_proxy, account, signer = await setup()

    l1_messages_sender = 0xbeaf
    l1_headers_store_addr = 0xdead
    owner = account.contract_address
    await signer.send_transaction(
        account, messages_proxy.contract_address, 'initialize', [l1_messages_sender, l1_headers_store_addr, owner])

    new_account, new_signer = await create_account(starknet)
    with pytest.raises(StarkException):
        await new_signer.send_transaction(
        new_account, messages_proxy.contract_address, 'change_owner', [new_account.contract_address])
    

@pytest.mark.asyncio
async def test_change_owner():
    starknet, messages_proxy, account, signer = await setup()

    l1_messages_sender = 0xbeaf
    l1_headers_store_addr = 0xdead
    owner = account.contract_address
    await signer.send_transaction(
        account, messages_proxy.contract_address, 'initialize', [l1_messages_sender, l1_headers_store_addr, owner])

    new_owner = 0xbeaf
    await signer.send_transaction(
        account, messages_proxy.contract_address, 'change_owner', [new_owner])
    
    set_owner_call = await messages_proxy.get_owner().call()
    assert set_owner_call.result.res == new_owner

@pytest.mark.asyncio
async def test_initializer():
    starknet, messages_proxy, account, signer = await setup()

    l1_messages_sender = 0xbeaf
    l1_headers_store_addr = 0xdead
    owner = account.contract_address
    await signer.send_transaction(
        account, messages_proxy.contract_address, 'initialize', [l1_messages_sender, l1_headers_store_addr, owner])

    set_l1_messages_sender_call = await messages_proxy.get_l1_messages_sender().call()
    assert set_l1_messages_sender_call.result.res == l1_messages_sender

    set_l1_headers_store_addr_call = await messages_proxy.get_l1_headers_store_addr().call()
    assert set_l1_headers_store_addr_call.result.res == l1_headers_store_addr

    set_owner_call = await messages_proxy.get_owner().call()
    assert set_owner_call.result.res == owner

@pytest.mark.asyncio
async def test_change_contract_addresses_invalid_caller():
    starknet, messages_proxy, account, signer = await setup()

    l1_messages_sender = 0xbeaf
    l1_headers_store_addr = 0xdead
    owner = account.contract_address
    await signer.send_transaction(
        account, messages_proxy.contract_address, 'initialize', [l1_messages_sender, l1_headers_store_addr, owner])
    
    new_account, new_signer = await create_account(starknet)
    with pytest.raises(StarkException):
        await new_signer.send_transaction(
        new_account, messages_proxy.contract_address, 'change_contract_addresses', [0xdada, 0xfefe])
