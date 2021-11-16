// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.9;

interface IStarknetCore {
    /**
      Sends a message to an L2 contract.
    */
    function sendMessageToL2(
        uint256 to_address,
        uint256 selector,
        uint256[] calldata payload
    ) external;

    /**
      Consumes a message that was sent from an L2 contract.
    */
    function consumeMessageFromL2(uint256 fromAddress, uint256[] calldata payload) external;
}

contract L1MessagesSender {
    IStarknetCore public immutable starknetCore;
    uint256 public immutable l2RecipientAddr;

    uint256 constant SUBMIT_L1_BLOCKHASH_SELECTOR =
        0x1d10503b9f4c7f4bb8f0b639ec987e6ffb203184507406bc0c0a591189f00ec;

    constructor(IStarknetCore starknetCore_, uint256 l2RecipientAddr_) {
        starknetCore = starknetCore_;
        l2RecipientAddr = l2RecipientAddr_;
    }

    function sendExactBlockHashToL2(uint256 blockNumber_) external {
        bytes32 blockHash = blockhash(blockNumber_);
        require(blockHash != bytes32(0), "ERR_INVALID_BLOCK_NUMBER");
        _sendBlockHashToL2(blockHash);
    }

    function sendLatestBlockHashToL2() external {
        bytes32 blockHash = blockhash(block.number - 1);
        _sendBlockHashToL2(blockHash);
    }

    function _sendBlockHashToL2(bytes32 blockHash_) internal {
        uint256[] memory message = new uint256[](1);
        message[0] = uint256(blockHash_);
        starknetCore.sendMessageToL2(l2RecipientAddr, SUBMIT_L1_BLOCKHASH_SELECTOR, message);
    }
}
