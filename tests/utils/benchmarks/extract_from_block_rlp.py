from typing import Callable, List, Tuple

input = [17942930940933183180, 10630688908008413652, 12661074544460729427, 864726895158924156, 16160421152376605773, 16780068465932993973, 7473385843023090245, 1987365566732607810, 18248819419131476918, 1984847897903778775, 11250872762094254827, 2927235116766469468, 12571860411242042658, 16186457246499692536, 5430745597336979773, 4560371398778244901, 4180223512850766399, 11269249778585820866, 17452780617349289056, 17686478862929260379, 11152982928411641007, 17273895561864136137, 6175259058000229345, 15391611023919743232, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9545095912481861326, 10989761733450733549, 14953183967168469464, 9439837342822524276, 7532384104041296183, 3328588300275316088, 11561634209445742650, 1195534606310635284, 13885345432711804137, 13993844412326043916, 254522925965248994, 13959192]


def extract_from_block_rlp(rlp: List[int], bit_pos: int, size_bits: int) -> List[int]:
    start_word, start_pos = divmod(bit_pos, 64)

    left_shift = start_pos
    right_shift = 64 - left_shift

    full_words_affected, remainer = divmod(size_bits, 64)
    words_affected = full_words_affected if remainer == 0 else full_words_affected + 1

    new_words_chunks: List[Tuple[int, int]] = []
    for i in range(words_affected):
        left_part = rlp[start_word + i] << left_shift
        right_part = rlp[start_word + i + 1] >> right_shift
        new_words_chunks.append((left_part, right_part))

    merge_pair: Callable[[Tuple[int, int]], int] = lambda pair: (pair[0] | pair[1]) & (2**(64)-1)
    new_words: List[int] = list(map(merge_pair, new_words_chunks))

    return new_words

# parent_hash_words = extract_from_block_rlp(input, 32, 32 * 8)
parent_hash_words = extract_from_block_rlp(input, 32, 32 * 8)
ommers_hash_words = extract_from_block_rlp(input, 32 + 256, 32 * 8)

print('0x' + ''.join(v.to_bytes(8, 'big').hex() for v in parent_hash_words))

print('0x' + ''.join(v.to_bytes(8, 'big').hex() for v in ommers_hash_words))


