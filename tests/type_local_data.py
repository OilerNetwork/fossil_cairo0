import pytest
from utils.types import Data


def test_from_nibbles_empty_array():
    input = []
    res = Data.from_nibbles(input)
    print(res)

def test_from_nibbles_odd_len():
    input = [3, 5, 2, 5, 6]
    with pytest.raises(Exception):
        res = Data.from_nibbles(input)

def test_from_nibbles_even_len_2():
    input = [3, 5]
    res = Data.from_nibbles(input)

def test_from_nibbles_even_len_6():
    input = [3, 5, 8, 7, 4, 7]
    res = Data.from_nibbles(input)

    

