import pytest
from utils.types import Data, IntsSequence

#to_nibbles

def test_to_nibbles_empty_array():
    input = []
    res = Data.from_nibbles(input)
    assert res.to_nibbles() == input

def test_to_nibbles_odd_len():
    input = [3, 5, 2, 5, 6]
    res = Data.from_nibbles(input)
    assert res.to_nibbles() == input

def test_to_nibbles_even_len_2():
    input = [3, 5]
    res = Data.from_nibbles(input)
    assert res.to_nibbles() == input

def test_to_nibbles_even_len_6():
    input = [3, 5, 8, 7, 4, 7]
    res = Data.from_nibbles(input)
    assert res.to_nibbles() == input

#to_ints

def test_to_ints_empty_ints():
    input = IntsSequence([], 0)
    res = Data.from_ints(input)
    assert res.to_ints() == input

def test_to_ints_nonfull():
    input = IntsSequence([123], 1)
    res = Data.from_ints(input)
    assert res.to_ints() == input

def test_to_ints_leading_zeroes():
    input = IntsSequence([123], 2)
    res = Data.from_ints(input)
    assert res.to_ints() == input

def test_to_ints_just_zeroes():
    input = IntsSequence([0], 2)
    res = Data.from_ints(input)
    assert res.to_ints() == input

def test_to_ints_full_word():
    input = IntsSequence([12379813738877118345], 8)
    res = Data.from_ints(input)
    assert res.to_ints() == input

def test_to_ints_full_word_and_a_byte():
    input = IntsSequence([12379813738877118345,123], 9)
    res = Data.from_ints(input)
    assert res.to_ints() == input

def test_to_ints_two_full_words():
    input = IntsSequence([12379813738877118345,12379813738877118345], 16)
    res = Data.from_ints(input)
    assert res.to_ints() == input

#from_ints

def test_from_ints_empty_ints():
    input = IntsSequence([], 0)
    res = Data.from_ints(input)
    assert res.to_bytes() == b''

def test_from_ints_nonfull():
    input = IntsSequence([123], 1)
    res = Data.from_ints(input)
    assert res.to_bytes() == b'\x7B'

def test_from_ints_leading_zeroes():
    input = IntsSequence([123], 2)
    res = Data.from_ints(input)
    assert res.to_bytes() == b'\x00\x7B'

def test_from_ints_just_zeroes():
    input = IntsSequence([0], 2)
    res = Data.from_ints(input)
    assert res.to_bytes() == b'\x00\x00'

def test_from_ints_full_byte():
    input = IntsSequence([12379813738877118345], 8)
    res = Data.from_ints(input)
    assert res.to_bytes() == b'\xAB\xCD\xEF\x01\x23\x45\x67\x89'

def test_from_ints_full_byte_and_a_bit():
    input = IntsSequence([12379813738877118345,123], 9)
    res = Data.from_ints(input)
    assert res.to_bytes() == b'\xAB\xCD\xEF\x01\x23\x45\x67\x89\x7B'

def test_from_ints_two_full_bytes():
    input = IntsSequence([12379813738877118345,12379813738877118345], 16)
    res = Data.from_ints(input)
    assert res.to_bytes() == b'\xAB\xCD\xEF\x01\x23\x45\x67\x89\xAB\xCD\xEF\x01\x23\x45\x67\x89'

#from_hex

def test_from_hex_empty_hex():
    input = ''
    res = Data.from_hex(input)
    assert res.to_bytes() == b''

def test_from_hex_empty_0x_hex():
    input = '0x'
    res = Data.from_hex(input)
    assert res.to_bytes() == b''

def test_from_hex():
    input = '35abcd'
    res = Data.from_hex(input)
    assert res.to_bytes() == b'\x35\xab\xcd'

def test_from_0x_hex():
    input = '0x35abcd'
    res = Data.from_hex(input)
    assert res.to_bytes() == b'\x35\xab\xcd'

#from_bytes

def test_from_bytes_empty_bytes():
    input = b''
    res = Data.from_bytes(input)
    assert res.to_bytes() == input

def test_from_bytes():
    input = b'\x42\x42\x42'
    res = Data.from_bytes(input)
    assert res.to_bytes() == input

#from_nibbles

def test_from_nibbles_empty_array():
    input = []
    res = Data.from_nibbles(input)
    assert res.to_bytes() == b''

def test_from_nibbles_odd_len():
    input = [3, 5, 2, 5, 6]
    res = Data.from_nibbles(input)
    assert res.to_bytes() == b'\x03\x52\x56'

def test_from_nibbles_even_len_2():
    input = [3, 5]
    res = Data.from_nibbles(input)
    assert res.to_bytes() == b'\x35'

def test_from_nibbles_even_len_6():
    input = [3, 5, 8, 7, 4, 7]
    res = Data.from_nibbles(input)
    assert res.to_bytes() == b'\x35\x87\x47'

#from_int & to_int

def test_from_int_small():
    for input in range(0,69420):
        res = Data.from_int(input)
        assert res.to_int() == input

def test_from_int_maxfelt():
    input = 2**252 - 1
    res = Data.from_int(input)
    assert res.to_int() == input

def test_from_int_maxuint256():
    input = 2**256 - 1
    res = Data.from_int(input)
    assert res.to_int() == input
