// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.9;

import {FormatWords64} from "../lib/FormatWords64.sol";


contract TestFormatWords64 {
    function fromBytes32(bytes32 input) external pure returns(bytes8, bytes8, bytes8, bytes8) {
        return FormatWords64.fromBytes32(input);
    }
}