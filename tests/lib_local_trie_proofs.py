import pytest

from mocks.trie_proofs import trie_proofs

from utils.encode_proof import encode_proof
from utils.helpers import word64_to_nibbles, rlp_string_to_words64

from utils.benchmarks.trie_proofs import verify_account_proof

# @pytest.mark.asyncio
# async def test_encode_proof():
#     account_proof_rlp = encode_proof(trie_proofs[0]['accountProof'])
#     storage_proofs_rlp = list(map(lambda storage: encode_proof(storage['proof']), trie_proofs[0]['storageProof']))

# @pytest.mark.asyncio
# async def test_word64_to_bytes():
#     word = 12379813738319119365
#     word64_to_nibbles(word, 15)

# @pytest.mark.asyncio
# async def test_decode_proof_to_words():
#     account_proof_rlp = encode_proof(trie_proofs[0]['accountProof'])
#     account_proof_rlp_words = rlp_string_to_words64(account_proof_rlp)

@pytest.mark.asyncio
async def test_verify_invalid_account_proof():
    account = rlp_string_to_words64('0x78e05971af7857d6114f7f896f9fd58d5c5d18e5')
    root_hash = rlp_string_to_words64('0x96c4bdfb8f2ad089200bad93f6216fe96652f9e2761b55bfd8a715ad3d6ecaf6')
    with pytest.raises(Exception):
        verify_account_proof(account, root_hash, [])

@pytest.mark.asyncio
async def test_verify_invalid_account_proof():
    account = rlp_string_to_words64('0x78e05971af7857d6114f7f896f9fd58d5c5d18e5')
    root_hash = rlp_string_to_words64('0x96c4bdfb8f2ad089200bad93f6216fe96652f9e2761b55bfd8a715ad3d6ecaf6')
    node = trie_proofs[0]['storageProof'][0]['proof'][0]
    print(node)
    proof = [rlp_string_to_words64(node)]
    proof_lens = [int((len(node) - 2) / 2)]
    print(proof_lens)
    res = verify_account_proof(account, root_hash, proof, proof_lens)


