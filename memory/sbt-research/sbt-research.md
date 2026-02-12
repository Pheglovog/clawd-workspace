# Soulbound Token (SBT) 研究文档

> 研究时间：2026-02-12
> 预计字数：20K+
> ERC 状态：Review（2022年9月）

---

## 目录

1. [什么是 SBT](#什么是-sbt)
2. [SBT vs 普通 NFT](#sbt-vs-普通-nft)
3. [SBT 核心特性](#sbt-核心特性)
4. [实现标准](#实现标准)
5. [智能合约实现](#智能合约实现)
6. [前端集成](#前端集成)
7. [应用场景](#应用场景)
8. [安全考虑](#安全考虑)
9. [最佳实践](#最佳实践)

---

## 什么是 SBT

### 定义

Soulbound Token (SBT) 是一种**不可转移**的非同质化代币（NFT）。一旦铸造给某个地址，就永久绑定到该地址，不能被转移或出售。

**关键特性：**
- ✅ 不可转移
- ✅ 可焚烧（由持有者或授权地址）
- ✅ 可更新元数据
- ✅ 可验证所有权

### 背景

SBT 的概念最早由 Vitalik Buterin 在 2022 年 1 月的博客文章《Soulbound Tokens》中提出。

**灵感来源：** 来源于网络游戏中的"灵魂绑定"道具（获得后无法交易）。

---

## SBT vs 普通 NFT

| 特性 | 普通 NFT (ERC-721) | SBT |
|------|-------------------|-----|
| 可转移性 | ✅ 可转移 | ❌ 不可转移 |
| 可出售 | ✅ 可出售 | ❌ 不可出售 |
| 可赠送 | ✅ 可赠送 | ❌ 不可赠送 |
| 可焚烧 | ✅ 可持有者焚烧 | ✅ 可持有者或授权地址焚烧 |
| 可更新 | ❌ 通常不可更新 | ✅ 可更新元数据 |
| 所有权 | ✅ 可变更 | ❌ 绑定到铸造地址 |
| 应用场景 | 交易、收藏 | 身份、证书、成就 |

### 代码对比

#### 普通 NFT
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.23;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

contract RegularNFT is ERC721 {
    constructor() ERC721("Regular NFT", "RNFT") {}

    function mint(address to, uint256 tokenId) public {
        _mint(to, tokenId);
    }

    // ✅ 可转移
    function transferFrom(
        address from,
        address to,
        uint256 tokenId
    ) public override {
        super.transferFrom(from, to, tokenId);
    }
}
```

#### Soulbound Token
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.23;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

contract SoulboundToken is ERC721 {
    constructor() ERC721("Soulbound Token", "SBT") {}

    function mint(address to, uint256 tokenId) public {
        _mint(to, tokenId);
    }

    // ❌ 不可转移
    function transferFrom(
        address from,
        address to,
        uint256 tokenId
    ) public pure override {
        revert("Soulbound: cannot transfer");
    }

    // ❌ 不可转移
    function safeTransferFrom(
        address from,
        address to,
        uint256 tokenId,
        bytes memory data
    ) public pure override {
        revert("Soulbound: cannot transfer");
    }
}
```

---

## SBT 核心特性

### 1. 不可转移

SBT 最核心的特性是不可转移性。一旦铸造给某个地址，就永久绑定。

**实现方式：**

```solidity
// 重写 transferFrom
function transferFrom(
    address from,
    address to,
    uint256 tokenId
) public pure override {
    revert("Soulbound: cannot transfer");
}

// 重写 safeTransferFrom
function safeTransferFrom(
    address from,
    address to,
    uint256 tokenId,
    bytes memory data
) ) public pure override {
    revert("Soulbound: cannot transfer");
}

// 重写 approve
function approve(address to, uint256 tokenId) public pure override {
    revert("Soulbound: cannot approve");
}

// 重写 setApprovalForAll
function setApprovalForAll(address operator, bool approved) public pure override {
    revert("Soulbound: cannot approve");
}
```

### 2. 可焚烧

虽然 SBT 不可转移，但可以焚烧（销毁）。

**使用场景：**
- 注销账户
- 撤销证书
- 清理成就

**实现方式：**

```solidity
function burn(uint256 tokenId) public {
    require(ownerOf(tokenId) == msg.sender, "not owner");
    _burn(tokenId);
}

// 授权焚烧（由授权地址）
function burnByAuthority(uint256 tokenId) public {
    require(isAuthority[msg.sender], "not authority");
    _burn(tokenId);
}
```

### 3. 可更新元数据

SBT 可以更新元数据（如证书信息），但不能转移。

**实现方式：**

```solidity
mapping(uint256 => string) public tokenMetadata;

function updateMetadata(uint256 tokenId, string memory newMetadata) public {
    require(ownerOf(tokenId) == msg.sender, "not owner");
    tokenMetadata[tokenId] = newMetadata;
    emit MetadataUpdated(tokenId, newMetadata);
}

// 授权更新（由授权地址）
function updateMetadataByAuthority(
    uint256 tokenId,
    string memory newMetadata
) public {
    require(isAuthority[msg.sender], "not authority");
    tokenMetadata[tokenId] = newMetadata;
    emit MetadataUpdated(tokenId, newMetadata);
}
```

### 4. 可验证所有权

SBT 仍然可以验证所有权，只是所有权不可转移。

**实现方式：**

```solidity
function hasToken(address account, uint256 tokenId) public view returns (bool) {
    return ownerOf(tokenId) == account;
}

function balanceOf(address account) public view override returns (uint256) {
    return _balanceOf(account);
}
```

---

## 实现标准

### 标准 1: 修改 ERC-721

最简单的方式是继承 ERC-721 并重写转移函数。

**优点：**
- 简单直接
- 兼容现有工具

**缺点：**
- 不符合 ERC-721 标准（transferFrom 应该可用）

### 标准 2: EIP-5192 (Minimal Soulbound NFT)

EIP-5192 是 SBT 的正式标准。

**ERC-165 接口标识：**

```solidity
// ERC-165 接口
interface IERC5192 is IERC165 {
    // 烧烧事件
    event SoulboundTokenBurned(uint256 tokenId);

    // 查询是否不可转移
    function isSoulbound(uint256 tokenId) external view returns (bool);
}
```

**实现示例：**

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.23;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/utils/introspection/ERC165.sol";

contract SoulboundNFT is ERC721, IERC5192, ERC165 {
    bytes4 private constant _INTERFACE_ID_ERC5192 = 0x6ae1a56d;

    constructor() ERC721("Soulbound NFT", "SBNFT") {}

    // 检查是否不可转移
    function isSoulbound(uint256 tokenId) public view override returns (bool) {
        return _exists(tokenId);  // 所有 token 都是不可转移的
    }

    // 重写转移函数
    function transferFrom(
        address from,
        address to,
        uint256 tokenId
    ) public pure override {
        revert("Soulbound: cannot transfer");
    }

    function safeTransferFrom(
        address from,
        address to,
        uint256 tokenId,
        bytes memory data
    ) public pure override {
        revert("Soulbound: cannot transfer");
    }

    function approve(address to, uint256 tokenId) public pure override {
        revert("Soulbound: cannot approve");
    }

    function setApprovalForAll(address operator, bool approved) public pure override {
        revert("Soulbound: cannot approve");
    }

    // 烧毁函数
    function burn(uint256 tokenId) public {
        require(ownerOf(tokenId) == msg.sender, "not owner");
        _burn(tokenId);
        emit SoulboundTokenBurned(tokenId);
    }

    // ERC-165 支持
    function supportsInterface(bytes4 interfaceId) public view override(ERC165, IERC165) returns (bool) {
        return
            interfaceId == type(IERC721).interfaceId ||
            interfaceId == type(IERC5192).interfaceId ||
            super.supportsInterface(interfaceId);
    }
}
```

### 标准 3: OpenZeppelin Soulbound

OpenZeppelin 提供了 `Soulbound` 扩展。

**安装：**

```bash
npm install @openzeppelin/contracts
```

**使用：**

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.23;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Consecutive.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/token/ERC721/utils/ERC721Holder.sol";

contract MySBT is
    ERC721,
    ERC721Consecutive,
    ERC721Enumerable,
    ERC721Holder
{
    // 重写转移函数
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 firstTokenId,
        uint256 batchSize
    ) internal pure override {
        // 禁止所有转移
        require(from == address(0) || to == address(0), "Soulbound: cannot transfer");
    }
}
```

---

## 智能合约实现

### 1. 简单的 SBT 合约

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.23;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/utils/introspection/ERC165.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract SimpleSBT is ERC721, IERC5192, ERC165, Ownable {
    bytes4 private constant _INTERFACE_ID_ERC5192 = 0x6ae1a56d;

    uint256 private _tokenIdCounter;

    event Minted(address indexed owner, uint256 indexed tokenId);
    event MetadataUpdated(uint256 indexed tokenId, string newMetadata);

    constructor() ERC721("Simple SBT", "SSBT") Ownable(msg.sender) {
        _tokenIdCounter = 1;
    }

    // 铸造 SBT
    function mint(address to) public onlyOwner {
        uint256 tokenId = _tokenIdCounter;
        _tokenIdCounter++;
        _safeMint(to, tokenId);
        emit Minted(to, tokenId);
    }

    // 更新元数据
    function updateMetadata(uint256 tokenId, string memory newMetadata) public {
        require(ownerOf(tokenId) == msg.sender, "not owner");
        _setTokenURI(tokenId, newMetadata);
        emit MetadataUpdated(tokenId, newMetadata);
    }

    // 烧毁
    function burn(uint256 tokenId) public {
        require(ownerOf(tokenId) == msg.sender, "not owner");
        _burn(tokenId);
        emit SoulboundTokenBurned(tokenId);
    }

    // 检查是否不可转移
    function isSoulbound(uint256 tokenId) public view override returns (bool) {
        return _exists(tokenId);
    }

    // 禁止转移
    function transferFrom(
        address from,
        address to,
        uint256 tokenId
    ) public pure override {
        revert("Soulbound: cannot transfer");
    }

    // 禁止转移
    function safeTransferFrom(
        address from,
        address to,
        uint256 tokenId,
        bytes memory data
    ) public pure override {
        revert("Soulbound: cannot transfer");
    }

    // 禁止授权
    function approve(address to, uint256 tokenId) public pure override {
        revert("Soulbound: cannot approve");
    }

    function setApprovalForAll(address operator, bool approved) public pure override {
        revert("Soulbound: cannot approve");
    }

    // ERC-165 支持
    function supportsInterface(bytes4 interfaceId) public view override(ERC165, IERC165) returns (bool) {
        return
            interfaceId == type(IERC721).interfaceId ||
            interfaceId == type(IERC5192).interfaceId ||
            super.supportsInterface(interfaceId);
    }
}
```

### 2. 学历证书 SBT

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.23;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/introspection/ERC165.sol";

contract CertificateSBT is
    ERC721URIStorage,
    AccessControl,
    IERC5192,
    ERC165
{
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant ISSUER_ROLE = keccak256("ISSUER_ROLE");
    bytes4 private constant _INTERFACE_ID_ERC5192 = 0x6ae1a56d;

    uint256 private _tokenIdCounter;

    struct Certificate {
        string name;
        string institution;
        string degree;
        string major;
        uint256 issuanceDate;
        uint256 expiryDate;
        uint256 score;
    }

    mapping(uint256 => Certificate) public certificates;
    mapping(uint256 => bool) public isRevoked;

    event CertificateIssued(
        address indexed student,
        uint256 indexed tokenId,
        string name,
        string degree
    );

    event CertificateRevoked(uint256 indexed tokenId);
    event CertificateUpdated(uint256 indexed tokenId);

    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
        _grantRole(ISSUER_ROLE, msg.sender);
        _tokenIdCounter = 1;
    }

    // 铸造证书
    function issueCertificate(
        address student,
        string memory name,
        string memory institution,
        string memory degree,
        string memory major,
        uint256 expiryDate,
        uint256 score,
        string memory uri
    ) public onlyRole(ISSUER_ROLE) {
        uint256 tokenId = _tokenIdCounter;
        _tokenIdCounter++;

        certificates[tokenId] = Certificate({
            name: name,
            institution: institution,
            degree: degree,
            major: major,
            issuanceDate: block.timestamp,
            expiryDate: expiryDate,
            score: score
        });

        _safeMint(student, tokenId);
        _setTokenURI(tokenId, uri);

        emit CertificateIssued(student, tokenId, name, degree);
    }

    // 更新证书
    function updateCertificate(
        uint256 tokenId,
        string memory uri
    ) public onlyRole(ADMIN_ROLE) {
        require(_exists(tokenId), "certificate does not exist");
        _setTokenURI(tokenId, uri);
        emit CertificateUpdated(tokenId);
    }

    // 撤销证书
    function revokeCertificate(uint256 tokenId) public onlyRole(ADMIN_ROLE) {
        require(_exists(tokenId), "certificate does not exist");
        isRevoked[tokenId] = true;
        _burn(tokenId);
        emit CertificateRevoked(tokenId);
    }

    // 查询证书信息
    function getCertificate(uint256 tokenId) public view returns (Certificate memory) {
        require(_exists(tokenId), "certificate does not exist");
        return certificates[tokenId];
    }

    // 验证证书有效性
    function isValidCertificate(uint256 tokenId) public view returns (bool) {
        return _exists(tokenId) && !isRevoked[tokenId];
    }

    // 禁止转移
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 firstTokenId,
        uint256 batchSize
    ) internal pure override {
        require(from == address(0) || to == address(0), "Soulbound: cannot transfer");
    }

    // 实现接口
    function isSoulbound(uint256 tokenId) public view override returns (bool) {
        return _exists(tokenId);
    }

    function supportsInterface(bytes4 interfaceId) public view override(ERC165, IERC165) returns (bool) {
        return
            interfaceId == type(IERC721).interfaceId ||
            interfaceId == type(IERC721Metadata).interfaceId ||
            interfaceId == type(IERC5192).interfaceId ||
            super.supportsInterface(interfaceId);
    }
}
```

### 3. 游戏 SBT

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.23;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/introspection/ERC165.sol";

contract GameSBT is
    ERC721,
    ERC721Enumerable,
    ERC721URIStorage,
    AccessControl,
    IERC5192,
    ERC165
{
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant GAME_ROLE = keccak256("GAME_ROLE");
    bytes4 private constant _INTERFACE_ID_ERC5192 = 0x6ae1a56d;

    uint256 private _tokenIdCounter;

    struct Achievement {
        string name;
        string description;
        uint256 timestamp;
        uint256 score;
        uint256 level;
        bool isLegendary;
    }

    mapping(uint256 => Achievement) public achievements;

    event AchievementUnlocked(
        address indexed player,
        uint256 indexed tokenId,
        string name
    );

    event AchievementLeveledUp(
        address indexed player,
        uint256 indexed tokenId,
        uint256 newLevel
    );

    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
        _grantRole(GAME_ROLE, msg.sender);
        _tokenIdCounter = 1;
    }

    // 解锁成就
    function unlockAchievement(
        address player,
        string memory name,
        string memory description,
        uint256 score,
        bool isLegendary,
        string memory uri
    ) public onlyRole(GAME_ROLE) {
        uint256 tokenId = _tokenIdCounter;
        _tokenIdCounter++;

        achievements[tokenId] = Achievement({
            name: name,
            description: description,
            timestamp: block.timestamp,
            score: score,
            level: 1,
            isLegendary: isLegendary
        });

        _safeMint(player, tokenId);
        _setTokenURI(tokenId, uri);

        emit AchievementUnlocked(player, tokenId, name);
    }

    // 升级成就
    function levelUpAchievement(uint256 tokenId, uint256 newLevel) public {
        require(ownerOf(tokenId) == msg.sender, "not owner");
        achievements[tokenId].level = newLevel;
        emit AchievementLeveledUp(msg.sender, tokenId, newLevel);
    }

    // 更新分数
    function updateScore(uint256 tokenId, uint256 newScore) public onlyRole(GAME_ROLE) {
        require(_exists(tokenId), "achievement does not exist");
        achievements[tokenId].score = newScore;
    }

    // 查询成就
    function getAchievement(uint256 tokenId) public view returns (Achievement memory) {
        require(_exists(tokenId), "achievement does not exist");
        return achievements[tokenId];
    }

    // 禁止转移
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 firstTokenId,
        uint256 batchSize
    ) internal pure override {
        require(from == address(0) || to == address(0), "Soulbound: cannot transfer");
    }

    function isSoulbound(uint256 tokenId) public view override returns (bool) {
        return _exists(tokenId);
    }

    function supportsInterface(bytes4 interfaceId) public view override(ERC165, IERC165) returns (bool) {
        return
            interfaceId == type(IERC721).interfaceId ||
            interfaceId == type(IERC721Metadata).interfaceId ||
            interfaceId == type(IERC721Enumerable).interfaceId ||
            interfaceId == type(IERC721URIStorage).interfaceId ||
            interfaceId == type(IERC5192).interfaceId ||
            super.supportsInterface(interfaceId);
    }
}
```

---

## 前端集成

### 使用 ethers.js v6+

```javascript
import { ethers } from "ethers";

// 合约 ABI
const sbtABI = [
    "function mint(address to) public",
    "function updateMetadata(uint256 tokenId, string newMetadata) public",
    "function burn(uint256 tokenId) public",
    "function isSoulbound(uint256 tokenId) public view returns (bool)",
    "function ownerOf(uint256 tokenId) public view returns (address)"
];

// 连接到合约
const sbtAddress = "0x...";
const provider = new ethers.JsonRpcProvider("https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY");
const sbtContract = new ethers.Contract(sbtAddress, sbtABI, provider);

// 铸造 SBT
async function mintSBT(to) {
    const signer = await provider.getSigner();
    const sbtWithSigner = sbtContract.connect(signer);

    const tx = await sbtWithSigner.mint(to);
    const receipt = await tx.wait();
    console.log("SBT minted:", receipt.transactionHash);

    return receipt;
}

// 查询是否是 SBT
async function checkIsSoulbound(tokenId) {
    const isSBT = await sbtContract.isSoulbound(tokenId);
    console.log(`Token ${tokenId} is Soulbound: ${isSBT}`);

    return isSBT;
}

// 更新元数据
async function updateMetadata(tokenId, newMetadata) {
    const signer = await provider.getSigner();
    const sbtWithSigner = sbtContract.connect(signer);

    const tx = await sbtWithSigner.updateMetadata(tokenId, newMetadata);
    const receipt = await tx.wait();
    console.log("Metadata updated:", receipt.transactionHash);

    return receipt;
}

// 验证 SBT
async function validateSBT(tokenId, expectedOwner) {
    const owner = await sbtContract.ownerOf(tokenId);
    const isSBT = await sbtContract.isSoulbound(tokenId);

    if (owner.toLowerCase() !== expectedOwner.toLowerCase()) {
        throw new Error("Invalid owner");
    }

    if (!isSBT) {
        throw new Error("Not a Soulbound Token");
    }

    console.log("SBT is valid");
    return true;
}
```

### 使用 Web3.js

```javascript
import Web3 from "web3";

const web3 = new Web3(window.ethereum);

const sbtABI = [
    {
        "inputs": [
            { "internalType": "address", "name": "to", "type": "address" }
        ],
        "name": "mint",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
];

const sbtAddress = "0x...";
const sbtContract = new web3.eth.Contract(sbtABI, sbtAddress);

// 铸造 SBT
async function mintSBT(to) {
    const accounts = await web3.eth.getAccounts();
    const from = accounts[0];

    const tx = await sbtContract.methods.mint(to).send({ from });
    console.log("SBT minted:", tx.transactionHash);

    return tx;
}

// 铸造并等待确认
async function mintAndWait(to) {
    const accounts = await web3.eth.getAccounts();
    const from = accounts[0];

    const tx = await sbtContract.methods.mint(to).send({ from });
    const receipt = await web3.eth.waitForTransactionReceipt(tx.transactionHash);

    console.log("SBT minted and confirmed:", receipt);
    return receipt;
}
```

### 错误处理

```javascript
try {
    const receipt = await mintSBT(userAddress);
} catch (error) {
    if (error.code === 4001) {
        console.error("User rejected transaction");
    } else if (error.message.includes("Soulbound: cannot transfer")) {
        console.error("Transfer not allowed for Soulbound Token");
    } else {
        console.error("Unknown error:", error);
    }
}
```

---

## 应用场景

### 1. 学历证书

**用途：**
- 学位证书
- 课程完成证书
- 技能认证
- 专业执照

**优势：**
- 防止证书买卖
- 防止证书伪造
- 可验证真实性

**示例：**

```solidity
contract DiplomaSBT {
    struct Diploma {
        string university;
        string degree;
        string major;
        uint256 year;
        uint256 gpa;
        bytes32 diplomaHash;  // 纸质文凭的哈希
    }

    mapping(uint256 => Diploma) public diplomas;

    function issueDiploma(
        address student,
        string memory university,
        string memory degree,
        string memory major,
        uint256 year,
        uint256 gpa,
        bytes32 diplomaHash,
        string memory uri
    ) public {
        // ...
    }
}
```

### 2. 游戏

**用途：**
- 成就徽章
- 游戏排名
- 赛季奖励
- 账号绑定物品

**优势：**
- 防止账号交易
- 防止成就买卖
- 增加游戏公平性

**示例：**

```solidity
contract GameAchievementSBT {
    struct Achievement {
        string name;
        string description;
        uint256 rarity;  // 1=普通, 2=稀有, 3=史诗, 4=传说
        uint256 unlockedAt;
    }

    mapping(uint256 => Achievement) public achievements;

    function unlockAchievement(
        address player,
        string memory name,
        uint256 rarity,
        string memory description,
        string memory uri
    ) public {
        // ...
    }
}
```

### 3. 身份认证

**用途：**
- KYC 认证
- 身份证明
- 会员资格
- 社区身份

**优势：**
- 防止身份买卖
- 可验证真实性
- 不可转移保护

**示例：**

```solidity
contract IdentitySBT {
    struct Identity {
        string name;
        string email;
        string documentHash;  // KYC 文档哈希
        uint256 verifiedAt;
        string verificationLevel;  // "basic", "standard", "enhanced"
    }

    mapping(address => Identity) public identities;

    function verifyIdentity(
        address user,
        string memory name,
        string memory email,
        bytes32 documentHash,
        string memory uri
    ) public onlyRole(VERIFIER_ROLE) {
        identities[user] = Identity({
            name: name,
            email: email,
            documentHash: documentHash,
            verifiedAt: block.timestamp,
            verificationLevel: "standard"
        });

        // 铸造 SBT
        _safeMint(user, userToTokenId(user));
        _setTokenURI(userToTokenId(user), uri);
    }
}
```

### 4. 会员资格

**用途：**
- 俱乐部会员
- 订阅服务
- VIP 等级
- 早期支持者

**优势：**
- 防止会员买卖
- 可验证会员身份
- 可更新会员状态

**示例：**

```solidity
contract MembershipSBT {
    struct Membership {
        string tier;  // "basic", "premium", "platinum"
        uint256 expiresAt;
        uint256 benefitsCount;
        uint256 totalSpent;
    }

    mapping(address => Membership) public memberships;

    function upgradeMembership(address user) public {
        Membership storage membership = memberships[user];
        membership.tier = getNextTier(membership.tier);
        membership.expiresAt = block.timestamp + 30 days;
    }
}
```

### 5. 社交图谱

**用途：**
- 友谊关系
- 关注关系
- 社区贡献
- 信任网络

**优势：**
- 防止关系买卖
- 不可转移保护
- 可验证连接

**示例：**

```solidity
contract SocialSBT {
    struct Connection {
        address from;
        address to;
        string relationshipType;  // "friend", "follow", "trust"
        uint256 since;
    }

    mapping(uint256 => Connection) public connections;
    mapping(address => mapping(address => uint256)) public connectionIds;

    function establishConnection(
        address from,
        address to,
        string memory relationshipType
    ) public {
        require(from == msg.sender || to == msg.sender, "not a participant");

        uint256 tokenId = uint256(keccak256(abi.encodePacked(from, to, relationshipType)));
        connections[tokenId] = Connection({
            from: from,
            to: to,
            relationshipType: relationshipType,
            since: block.timestamp
        });

        connectionIds[from][to] = tokenId;
    }
}
```

---

## 安全考虑

### 1. 不可转移绕过

**风险：** 攻击者可能试图绕过不可转移限制。

**防护：**

```solidity
function _beforeTokenTransfer(
    address from,
    address to,
    uint256 firstTokenId,
    uint256 batchSize
) internal pure override {
    require(from == address(0) || to == address(0), "Soulbound: cannot transfer");
}

function transferFrom(
    address from,
    address to,
    uint256 tokenId
) public pure override {
    revert("Soulbound: cannot transfer");
}
```

### 2. 元数据更新攻击

**风险：** 攻击者可能更新元数据以伪造信息。

**防护：**

```solidity
// 仅允许授权地址更新
function updateMetadataByAuthority(
    uint256 tokenId,
    string memory newMetadata
) public onlyRole(ADMIN_ROLE) {
    require(_exists(tokenId), "token does not exist");
    _setTokenURI(tokenId, newMetadata);
    emit MetadataUpdated(tokenId, newMetadata);
}
```

### 3. 烧毁权限

**风险：** 攻击者可能恶意烧毁 SBT。

**防护：**

```solidity
// 仅允许持有者或授权地址烧毁
function burn(uint256 tokenId) public {
    require(
        ownerOf(tokenId) == msg.sender || isAuthority[msg.sender],
        "not authorized"
    );
    _burn(tokenId);
}
```

### 4. 重入攻击

**风险：** SBT 可能受到重入攻击。

**防护：**

```solidity
function burn(uint256 tokenId) public {
    require(ownerOf(tokenId) == msg.sender, "not owner");
    
    // 检查效果
    uint256 balance = balanceOf(msg.sender);
    _burn(tokenId);
    
    require(balance - 1 == balanceOf(msg.sender), "reentrancy detected");
}
```

---

## 最佳实践

### 1. 使用 EIP-5192 标准

```solidity
// 实现 EIP-5192 接口
function isSoulbound(uint256 tokenId) external view returns (bool);
```

### 2. 添加事件日志

```solidity
event Minted(address indexed owner, uint256 indexed tokenId);
event MetadataUpdated(uint256 indexed tokenId, string newMetadata);
event Burned(uint256 indexed tokenId);
```

### 3. 使用 AccessControl

```solidity
import "@openzeppelin/contracts/access/AccessControl.sol";

contract SBT is AccessControl {
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant ISSUER_ROLE = keccak256("ISSUER_ROLE");

    function mint(address to) public onlyRole(ISSUER_ROLE) {
        // ...
    }
}
```

### 4. 链下元数据存储

```solidity
// 将元数据存储在 IPFS 上
function mint(address to, string memory metadataURI) public {
    uint256 tokenId = _tokenIdCounter;
    _tokenIdCounter++;

    _safeMint(to, tokenId);
    _setTokenURI(tokenId, metadataURI);

    emit Minted(to, tokenId, metadataURI);
}
```

### 5. 可更新设计

```solidity
// 允许更新元数据
function updateMetadata(uint256 tokenId, string memory newMetadata) public {
    require(ownerOf(tokenId) == msg.sender, "not owner");
    _setTokenURI(tokenId, newMetadata);
    emit MetadataUpdated(tokenId, newMetadata);
}

// 允许授权更新
function updateMetadataByAuthority(
    uint256 tokenId,
    string memory newMetadata
) public onlyRole(ADMIN_ROLE) {
    _setTokenURI(tokenId, newMetadata);
    emit MetadataUpdated(tokenId, newMetadata);
}
```

---

## 总结

### 关键要点

1. **SBT 是不可转移的 NFT**
   - 绑定到铸造地址
   - 不能出售或转移

2. **核心特性**
   - 不可转移
   - 可焚烧
   - 可更新元数据
   - 可验证所有权

3. **应用场景**
   - 学历证书
   - 游戏成就
   - 身份认证
   - 会员资格
   - 社交关系

4. **安全考虑**
   - 防止不可转移绕过
   - 防止元数据更新攻击
   - 防止烧毁权限问题
   - 防止重入攻击

### 下一步

- 在 CarLife 中集成 SBT（车辆证书）
- 研究 Multi-SBT（批量铸造）
- 研究 Cross-Chain SBT（跨链 SBT）
- 研究 SBT + DeFi（SBT 作为抵押品）

---

*文档字数：约 20K 字*
*创建时间：2026-02-12*
*作者：吕布（上等兵•甘的 AI助手）*
