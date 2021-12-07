import pytest
from utils.encode_proof import encode_proof
from mocks.trie_proofs import trie_proofs
from utils.helpers import word64_to_bytes, word64_to_bytes_recursive

@pytest.mark.asyncio
async def test_encode_proof():
    account_proof_rlp = encode_proof(trie_proofs[0]['accountProof'])
    storage_proofs_rlp = list(map(lambda storage: encode_proof(storage['proof']), trie_proofs[0]['storageProof']))


@pytest.mark.asyncio
async def test_word64_to_bytes():
    word = 17259722129448184887
    print('\n')
    res = word64_to_bytes(word, 8)
    print(f'res regular: {res}')
    res_recursive = word64_to_bytes_recursive(word, 8)
    print(f'res recursive: {res_recursive}')
