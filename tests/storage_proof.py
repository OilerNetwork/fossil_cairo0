from hexbytes.main import HexBytes
import pytest
from typing import Callable

from starkware.starknet.testing.starknet import Starknet
from utils.create_account import create_account
from web3 import Web3


# The path to the contract source code.


# The testing library uses python's asyncio. So the following
# decorator and the ``async`` keyword are needed.
@pytest.mark.asyncio
async def test_submit_hash():
    # Create a new Starknet class that simulates the StarkNet
    # system.
    starknet = await Starknet.empty()

    # Deploy the storage proof contract.
    storage_proof = await starknet.deploy(source="contracts/starknet/L1StorageProof.cairo", cairo_path=["contracts"])

    # Create a default account to interact with the contract
    account, signer = await create_account(starknet)

    # Create a L1 messages relayer mock
    l1_relayer_account, l1_relayer_signer = account, signer = await create_account(starknet)

    # Initialize storage proof contract
    await signer.send_transaction(
        account, storage_proof.contract_address, 'initialize', [l1_relayer_account.contract_address], 0)

    # Submit message using l1_relayer_account
    message = Web3.keccak(text="hello world")
    chunked_message = [message[i:i+8] for i in range(0, len(message), 8)]

    assert len(chunked_message) == 4

    hexbyte_to_int: Callable[[HexBytes], int] = lambda word: int(word.hex(), 16)
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








    
