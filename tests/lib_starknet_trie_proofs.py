import pytest
from typing import NamedTuple

from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.testing.starknet import Starknet

class TestsDeps(NamedTuple):
    starknet: Starknet
    trie_proofs: StarknetContract


async def setup():
    starknet = await Starknet.empty()
    trie_proofs = await starknet.deploy(source="contracts/starknet/test/TestTrieProofs.cairo", cairo_path=["contracts"])
    return TestsDeps(
        starknet=starknet,
        trie_proofs=trie_proofs
    )


@pytest.mark.asyncio
async def test_count_shared_prefix_len():
    starknet, trie_proofs = await setup()