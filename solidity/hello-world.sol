pragma solidity ^0.8.20;

// SPDX-License-Identifier: MIT
contract HelloWorld {
    string public message = "Hello, World!";

    function setMessage(string memory newMessage) public {
        message = newMessage;
    }

    function getMessage() public view returns (string memory) {
        return message;
    }
}
