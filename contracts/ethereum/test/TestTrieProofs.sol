// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.9;


contract TestTrieProofs {
    function extractNibble(bytes32 path, uint256 position) public pure returns (uint8 nibble) {
        require(position < 64, "Invalid nibble position");
        bytes1 shifted = position == 0 ? bytes1(path >> 4) : bytes1(path << ((position - 1) * 4));
        return uint8(bytes1(uint8(shifted) & 0xF));
    }

    function decodeNibbles(bytes memory compact, uint skipNibbles) public pure returns (bytes memory nibbles) {
        require(compact.length > 0, "Empty bytes array");

        uint length = compact.length * 2;
        require(skipNibbles <= length, "Skip nibbles amount too large");
        length -= skipNibbles;

        nibbles = new bytes(length);
        uint nibblesLength = 0;

        for (uint i = skipNibbles; i < skipNibbles + length; i += 1) {
            if (i % 2 == 0) {
                nibbles[nibblesLength] = bytes1((uint8(compact[i/2]) >> 4) & 0xF);
            } else {
                nibbles[nibblesLength] = bytes1((uint8(compact[i/2]) >> 0) & 0xF);
            }
            nibblesLength += 1;
        }

        assert(nibblesLength == nibbles.length);
    }

    function merklePatriciaCompactDecode(bytes memory compact) public pure returns (bytes memory nibbles) {
        require(compact.length > 0, "Empty bytes array");
        uint first_nibble = uint8(compact[0]) >> 4 & 0xF;
        uint skipNibbles;
        if (first_nibble == 0) {
            skipNibbles = 2;
        } else if (first_nibble == 1) {
            skipNibbles = 1;
        } else if (first_nibble == 2) {
            skipNibbles = 2;
        } else if (first_nibble == 3) {
            skipNibbles = 1;
        } else {
            // Not supposed to happen!
            revert();
        }
        return decodeNibbles(compact, skipNibbles);
    }

    function sharedPrefixLength(uint xsOffset, bytes memory xs, bytes memory ys) public pure returns (uint) {
        uint256 i = 0;
        for (i = 0; i + xsOffset < xs.length && i < ys.length; i++) {
            if (xs[i + xsOffset] != ys[i]) {
                return i;
            }
        }
        return i;
    }
}