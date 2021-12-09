pragma solidity 0.8.9;

import {IStarknetCore} from "../interfaces/IStarknetCore.sol";


contract StarknetCoreMock is IStarknetCore {
    event MessageSentToL2(uint256 toAddress, uint256 selector, uint256[] payload);
    event MessageReceivedFromL2(uint256 fromAddress, uint256[] payload);

    function sendMessageToL2(
        uint256 to_address,
        uint256 selector,
        uint256[] calldata payload
    ) external {
        emit MessageSentToL2(to_address, selector, payload);
    }

    function consumeMessageFromL2(uint256 fromAddress, uint256[] calldata payload) external {
        emit MessageReceivedFromL2(fromAddress, payload);
    }

}