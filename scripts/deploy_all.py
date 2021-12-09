import os
import web3
import pytest
from services.external_api.base_client import RetryConfig

from starkware.starknet.services.api.gateway.gateway_client import GatewayClient
from starkware.starknet.services.api.gateway.transaction import Deploy
from starkware.starknet.services.api.contract_definition import ContractDefinition
from starkware.starkware_utils.error_handling import StarkErrorCode
from starkware.starknet.definitions import fields


def get_gateway_client(args) -> GatewayClient:
    gateway_url = os.environ.get("STARKNET_GATEWAY_URL")
    if args.gateway_url is not None:
        gateway_url = args.gateway_url
    if gateway_url is None:
        raise Exception(
            f'gateway_url must be specified with the "{args.command}" subcommand.\n'
            "Consider passing --network or setting the STARKNET_NETWORK environment variable."
        )
    # Limit the number of retries.
    retry_config = RetryConfig(n_retries=1)
    return GatewayClient(url=gateway_url, retry_config=retry_config)

@pytest.mark.asyncio
async def main():
    # TODO pass args
    gateway_client = get_gateway_client()

    msg_contract_definition = ContractDefinition.loads('contracts/starknet/L1MessagesProxy.cairo')
    msg_dep_contract_tx = Deploy(
        contract_address_salt=fields.ContractAddressSalt.get_random_value(),
        contract_definition=msg_contract_definition,
        constructor_calldata=[],
    )
    msg_dep_gateway_response = await gateway_client.add_transaction(tx=msg_dep_contract_tx)
    l2_msg_contract_address = int(msg_dep_gateway_response["address"], 16)
    assert (msg_dep_gateway_response["code"] == StarkErrorCode.TRANSACTION_RECEIVED.name)

    headers_contract_definition = ContractDefinition.loads('contracts/starknet/L1HeadersStore.cairo')
    headers_dep_contract_tx = Deploy(
        contract_address_salt=fields.ContractAddressSalt.get_random_value(),
        contract_definition=headers_contract_definition,
        constructor_calldata=[],
    )
    headers_dep_gateway_response = await gateway_client.add_transaction(tx=headers_dep_contract_tx)
    l2_headers_contract_address = int(headers_dep_gateway_response["address"], 16)
    assert (headers_dep_gateway_response["code"] == StarkErrorCode.TRANSACTION_RECEIVED.name)

    # TODO L1 deployements using web3.py?




