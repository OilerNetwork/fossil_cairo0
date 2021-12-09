// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.9;

library FormatWords64 {
    function fromBytes32(bytes32 input) internal pure returns(bytes8 word1, bytes8 word2, bytes8 word3, bytes8 word4) {
        assembly {
            word1 := input
            word2 := shl(64, input)
            word3 := shl(128, input)
            word4 := shl(192, input)
        }
    }
}

