# def getRlpLength(rlp: List[int]) -> RLPValue:
#     firstByte = extractData(rlp, 0, 1)[0]

#     if firstByte < 192:
#         raise Exception("Wrong first byte in RLP")

#     if firstByte <= 247:
#         return RLPValue(firstByte - 192, 1)
#     else:
#         length_of_length = firstByte - 247
#         length = extractData(rlp, 1, length_of_length)[0] #this will fit in 8 bytes always
#         return RLPValue(length, 1+length_of_length)

# def getRlpStart(rlp: List[int]) -> int:
#     firstByte = extractData(rlp, 0, 1)[0]

#     if firstByte < 192:
#         raise Exception("Wrong first byte in RLP")

#     if firstByte <= 247:
#         return 1
#     else:
#         length_of_length = firstByte - 247
#         return 1+length_of_length