from typing import List
from utils.rlp import extractData, extractElement, jumpOverElement
from utils.types import IntsSequence


# idx  Element                 element length with 1 byte storing its length
# ==========================================================================

# Static elements (always same size):
# 0    RLP length              1+2
# 1    parentHash              1+32
# 2    ommersHash              1+32
# 3    beneficiary             1+20
# 4    stateRoot               1+32
# 5    TransactionRoot         1+32
# 6    receiptsRoot            1+32
#      logsBloom length        1+2
# 7    logsBloom               256
#                              =========

#  Total static elements size: 448 bytes

# Dynamic elements (need to read length) start at position 448
# and each one is preceeded with 1 byte length (if element is >= 128)
# or if element is < 128 - then length byte is skipped and it is just the 1-byte element:

# 8	difficulty  - starts at pos 448
# 9	number      - blockNumber
# 10	gasLimit
# 11	gasUsed
# 12	timestamp
# 13	extraData
# 14	mixHash
# 15	nonce

def getParentHash(rlp: List[int]) -> IntsSequence:
    return extractData(rlp, 4, 32)

def getOmmersHash(rlp: List[int]) -> IntsSequence:
    return extractData(rlp, 4+32+1, 32)

def getBeneficiary(rlp: List[int]) -> IntsSequence:
    return extractData(rlp, 4+32+1+32+1, 20)

def getStateRoot(rlp: List[int]) -> IntsSequence:
    return extractData(rlp, 4+32+1+32+1+20+1, 32)

def getTransactionsRoot(rlp: List[int]) -> IntsSequence:
    return extractData(rlp, 4+32+1+32+1+20+1+32+1, 32)

def getReceiptsRoot(rlp: List[int]) -> IntsSequence:
    return extractData(rlp, 4+32+1+32+1+20+1+32+1+32+1, 32)

def getDifficulty(rlp: List[int]) -> int:
    return extractElement(rlp, 448).values[0]

def getBlocknumber(rlp: List[int]) -> int:
    #jump over difficulty
    blockNumberPosition = jumpOverElement(rlp, 448)
    return extractElement(rlp, blockNumberPosition).values[0]

def getGasLimit(rlp: List[int]) -> int:
    #jump over difficulty
    blockNumberPosition = jumpOverElement(rlp, 448)
    #jump over blockNumber
    gasLimitPosition = jumpOverElement(rlp, blockNumberPosition)

    return extractElement(rlp, gasLimitPosition).values[0]

def getGasUsed(rlp: List[int]) -> int:
    #jump over difficulty
    blockNumberPosition = jumpOverElement(rlp, 448)
    #jump over blockNumber
    gasLimitPosition = jumpOverElement(rlp, blockNumberPosition)
    #jump over gasLimit
    gasUsedPosition = jumpOverElement(rlp, gasLimitPosition)

    return extractElement(rlp, gasUsedPosition).values[0]

def getTimestamp(rlp: List[int]) -> int:
    #jump over difficulty
    blockNumberPosition = jumpOverElement(rlp, 448)
    #jump over blockNumber
    gasLimitPosition = jumpOverElement(rlp, blockNumberPosition)
    #jump over gasLimit
    gasUsedPosition = jumpOverElement(rlp, gasLimitPosition)
    #jump over gasUsed
    timestampPosition = jumpOverElement(rlp, gasUsedPosition)

    return extractElement(rlp, timestampPosition).values[0]
