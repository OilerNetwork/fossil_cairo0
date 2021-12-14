import asyncio
import json
from services.external_api.base_client import RetryConfig

from starkware.starknet.services.api.gateway.gateway_client import GatewayClient
from starkware.starknet.services.api.gateway.transaction import Deploy, InvokeFunction
from starkware.starkware_utils.error_handling import StarkErrorCode
from starkware.starknet.definitions import fields
from starkware.starknet.compiler.compile import compile_starknet_files, get_selector_from_name

from web3 import Web3
from web3 import Account


def get_gateway_client(gateway_url: str) -> GatewayClient:
    # Limit the number of retries.
    retry_config = RetryConfig(n_retries=1)
    return GatewayClient(url=gateway_url, retry_config=retry_config)


async def main():
    secrets = json.load(open('secrets.json'))
    gateway_url = "https://alpha4.starknet.io/"
    eth_provider_url = f"https://eth-goerli.alchemyapi.io/v2/{secrets['alchemy_api_key']}"

    starknet_core_addr = '0xde29d060D45901Fb19ED6C6e959EB22d8626708e'
    gateway_client = get_gateway_client(gateway_url)

    # msg_contract_definition = ContractDefinition.loads('contracts/starknet/L1MessagesProxy.cairo')
    msg_dep_contract_tx = Deploy(
        contract_address_salt=fields.ContractAddressSalt.get_random_value(),
        constructor_calldata=[],
        contract_definition=compile_starknet_files(
                files=['contracts/starknet/L1MessagesProxy.cairo'], debug_info=True, cairo_path=['contracts']
            )
    )

    msg_dep_gateway_response = await gateway_client.add_transaction(tx=msg_dep_contract_tx)
    l2_msg_contract_address = int(msg_dep_gateway_response["address"], 16)
    assert (msg_dep_gateway_response["code"] == StarkErrorCode.TRANSACTION_RECEIVED.name)

    headers_dep_contract_tx = Deploy(
        contract_address_salt=fields.ContractAddressSalt.get_random_value(),
        constructor_calldata=[],
        contract_definition=compile_starknet_files(
                files=['contracts/starknet/L1HeadersStore.cairo'], debug_info=True, cairo_path=['contracts']
            )
    )
    headers_dep_gateway_response = await gateway_client.add_transaction(tx=headers_dep_contract_tx)
    l2_headers_contract_address = int(headers_dep_gateway_response["address"], 16)
    assert (headers_dep_gateway_response["code"] == StarkErrorCode.TRANSACTION_RECEIVED.name)

    # Load compiled contract's bytecode and abi
    f = open('build/contracts/L1MessagesSender.json')
    contract_build = json.load(f)
    w3 = Web3(Web3.HTTPProvider(eth_provider_url))

    deployer_priv_key = secrets['l1_priv_key']
    account = Account.from_key(deployer_priv_key)
    # Load deployer account
    w3.eth.default_account = account

    # Deploy
    L1MessagesSender = w3.eth.contract(abi=contract_build['abi'], bytecode=contract_build['bytecode'])
    deployment_tx = L1MessagesSender.constructor(starknet_core_addr, l2_msg_contract_address).buildTransaction({
        'from': account.address,
        'nonce': w3.eth.getTransactionCount(account.address),
        'gas': 2000000,
        'gasPrice': w3.toWei('20', 'gwei')
    })

    signed = account.sign_transaction(deployment_tx)
    tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction).hex()
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    l1_contract_addr = tx_receipt.contractAddress

    l2_headers_contract_init_tx = InvokeFunction(
            contract_address=l2_headers_contract_address,
            entry_point_selector=get_selector_from_name('initialize'),
            calldata=[l2_msg_contract_address],
            signature=[])

    l2_msg_contract_owner = 7488483839384883

    l2_msg_contract_init_tx = InvokeFunction(
            contract_address=l2_msg_contract_address,
            entry_point_selector=get_selector_from_name('initialize'),
            calldata=[int(l1_contract_addr, 16), l2_headers_contract_address, l2_msg_contract_owner],
            signature=[])

    await gateway_client.add_transaction(l2_headers_contract_init_tx)
    await gateway_client.add_transaction(l2_msg_contract_init_tx)

    print('\n')
    print(f"L1: contract address: {l1_contract_addr}")
    print(f"Starknet: L1 headers contract address: {hex(l2_headers_contract_address)}")
    print(f"Starknet: L1 messages recipient: {hex(l2_msg_contract_address)}")

asyncio.run(main())

