from hexbytes.main import HexBytes
from rlp import Serializable, encode
from web3.types import BlockData
from rlp.sedes import (
    BigEndianInt,
    big_endian_int,
    Binary,
    binary,
)
from eth_utils import to_bytes
from web3 import Web3


address = Binary.fixed_length(20, allow_empty=True)
hash32 = Binary.fixed_length(32)
int256 = BigEndianInt(256)
trie_root = Binary.fixed_length(32, allow_empty=True)


class BlockHeader(Serializable):
    fields = (
        ('parentHash', hash32),
        ('unclesHash', hash32),
        ('coinbase', address),
        ('stateRoot', trie_root),
        ('transactionsRoot', trie_root),
        ('receiptsRoot', trie_root),
        ('logsBloom', int256),
        ('difficulty', big_endian_int),
        ('number', big_endian_int),
        ('gasLimit', big_endian_int),
        ('gasUsed', big_endian_int),
        ('timestamp', big_endian_int),
        ('extraData', binary),
        ('mixHash', binary),
        ('nonce', Binary(8, allow_empty=True)),
        ('baseFeePerGas', big_endian_int)
    )

    def hash(self) -> HexBytes:
        _rlp = encode(self)
        return Web3.keccak(_rlp)
    
    def raw_rlp(self) -> bytes:
        return encode(self)

def build_block_header(block: BlockData) -> BlockHeader:
    header = BlockHeader(
        block["parentHash"],
        block["sha3Uncles"],
        to_bytes(int(block["miner"], 16)),
        block["stateRoot"],
        block['transactionsRoot'],
        block["receiptsRoot"],
        int.from_bytes(block["logsBloom"], 'big'),
        block["difficulty"],
        block["number"],
        block["gasLimit"],
        block["gasUsed"],
        block["timestamp"],
        block["extraData"],
        block["mixHash"],
        block["nonce"],
        block["baseFeePerGas"]
    )
    return header

    