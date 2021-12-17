from typing import List
from utils.rlp import RLPElement


def to_rlp_element(rlp64: List[int]) -> RLPElement:
    return RLPElement([0], 0)