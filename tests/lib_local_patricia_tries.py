import pytest
from utils.encode_proof import encode_proof
from mocks.trie_proofs import trie_proofs
from utils.helpers import word64_to_nibbles

@pytest.mark.asyncio
async def test_encode_proof():
    account_proof_rlp = encode_proof(trie_proofs[0]['accountProof'])
    storage_proofs_rlp = list(map(lambda storage: encode_proof(storage['proof']), trie_proofs[0]['storageProof']))


@pytest.mark.asyncio
async def test_word64_to_bytes():
    word = 12379813738319119365
    print('\n')
    res = word64_to_nibbles(word, 15)
    print(res)
    
    
