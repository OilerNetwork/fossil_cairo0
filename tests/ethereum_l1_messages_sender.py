from brownie import accounts, network
from brownie.network.event import _decode_logs


def test_l1_messages_sender_deploys(L1MessagesSender):
    accounts[0].deploy(L1MessagesSender, accounts[0].address, 9847383783)

def test_send_exact_block_hash_to_l2(L1MessagesSender, StarknetCoreMock):
    starknet_core_mock = accounts[0].deploy(StarknetCoreMock)
    l2_contract_addr = 9847383783
    l1_messages_sender = accounts[0].deploy(L1MessagesSender, starknet_core_mock.address, l2_contract_addr)

    latest_block = network.web3.eth.blockNumber
    tx = l1_messages_sender.sendExactParentHashToL2(latest_block, {'from': accounts[0]})

    logs = _decode_logs(tx.logs)

def test_send_latest_exact_block_hash_to_l2(L1MessagesSender, StarknetCoreMock):
    starknet_core_mock = accounts[0].deploy(StarknetCoreMock)
    l2_contract_addr = 9847383783
    l1_messages_sender = accounts[0].deploy(L1MessagesSender, starknet_core_mock.address, l2_contract_addr)

    tx = l1_messages_sender.sendLatestParentHashToL2({'from': accounts[0]})
    logs = _decode_logs(tx.logs)
    

