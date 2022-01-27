from typing import List
from utils.rlp import extractData, extractDataFromRLPItem, extractElement, jumpOverElement, to_list
from utils.types import IntsSequence, BlockHeaderIndexes

def getParentHash(rlp: IntsSequence) -> IntsSequence:
    rlpList = to_list(rlp)
    return extractDataFromRLPItem(rlp, rlpList[BlockHeaderIndexes.PARENT_HASH])

def getOmmersHash(rlp: IntsSequence) -> IntsSequence:
    rlpList = to_list(rlp)
    return extractDataFromRLPItem(rlp, rlpList[BlockHeaderIndexes.OMMERS_HASH])

def getBeneficiary(rlp: IntsSequence) -> IntsSequence:
    rlpList = to_list(rlp)
    return extractDataFromRLPItem(rlp, rlpList[BlockHeaderIndexes.BENEFICIARY])

def getStateRoot(rlp: IntsSequence) -> IntsSequence:
    rlpList = to_list(rlp)
    return extractDataFromRLPItem(rlp, rlpList[BlockHeaderIndexes.STATE_ROOT])

def getTransactionsRoot(rlp: IntsSequence) -> IntsSequence:
    rlpList = to_list(rlp)
    return extractDataFromRLPItem(rlp, rlpList[BlockHeaderIndexes.TRANSACTION_ROOT])

def getReceiptsRoot(rlp: IntsSequence) -> IntsSequence:
    rlpList = to_list(rlp)
    return extractDataFromRLPItem(rlp, rlpList[BlockHeaderIndexes.RECEIPTS_ROOT])

def getDifficulty(rlp: IntsSequence) -> IntsSequence:
    rlpList = to_list(rlp)
    return extractDataFromRLPItem(rlp, rlpList[BlockHeaderIndexes.DIFFICULTY])

def getBlocknumber(rlp: IntsSequence) -> IntsSequence:
    rlpList = to_list(rlp)
    return extractDataFromRLPItem(rlp, rlpList[BlockHeaderIndexes.BLOCK_NUMBER])

def getGasLimit(rlp: IntsSequence) -> IntsSequence:
    rlpList = to_list(rlp)
    return extractDataFromRLPItem(rlp, rlpList[BlockHeaderIndexes.GAS_LIMIT])

def getGasUsed(rlp: IntsSequence) -> IntsSequence:
    rlpList = to_list(rlp)
    return extractDataFromRLPItem(rlp, rlpList[BlockHeaderIndexes.GAS_USED])

def getTimestamp(rlp: IntsSequence) -> IntsSequence:
    rlpList = to_list(rlp)
    return extractDataFromRLPItem(rlp, rlpList[BlockHeaderIndexes.TIMESTAMP])

def getBaseFee(rlp: IntsSequence) -> IntsSequence:
    rlpList = to_list(rlp)
    return extractDataFromRLPItem(rlp, rlpList[BlockHeaderIndexes.BASE_FEE])
