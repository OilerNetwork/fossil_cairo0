import pytest
from utils.encode_proof import encode_proof
from mocks.trie_proofs import trie_proofs

@pytest.mark.asyncio
async def test_encode_proof():
    res = encode_proof(trie_proofs[0]['accountProof'])