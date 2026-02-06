# 以太坊 EIP 标准深度研究

> **目标**: 系统性研究以太坊 EIP 标准，从核心协议升级到应用层规范，掌握每个 EIP 的设计原理和实现细节

---

## 📋 EIP 分类体系

### 1. 核心协议 EIP (Core)
- EIP-155: Simple replay attack protection
- EIP-1559: Fee market change for ETH 1.0 chain
- EIP-2930: Access lists for transaction gas cost reductions
- EIP-4844: Proto-Danksharding

### 2. 网络 EIP (Networking)
- EIP-868: Swarm hash in Enr
- EIP-2132: DNS over Ethereum

### 3. 接口 EIP (Interface)
- EIP-165: Standard Interface Detection
- EIP-1820: Pseudo-introspection registry contract

### 4. ERC 标准 (ERC - Ethereum Request for Comment)
- ERC-20: Token Standard
- ERC-721: Non-Fungible Token Standard
- ERC-1155: Multi-Token Standard
- ERC-4626: Tokenized Vault Standard
- ERC-4907: Rental NFT Standard

---

## 🪙 ERC-20: 代币标准

### 1. 标准接口

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    // ===================== 总量 =====================
    function totalSupply() external view returns (uint256);

    // ===================== 余额 =====================
    function balanceOf(address account) external view returns (uint256);

    // ===================== 转账 =====================
    function transfer(address recipient, uint256 amount) external returns (bool);
    function allowance(address owner, address spender) external view returns (uint256);
    function approve(address spender, uint256 amount) external returns (bool);
    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);

    // ===================== 事件 =====================
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
}
```

**设计原理**:
- ✅ **总量固定**: `totalSupply` 在创建时设置，之后不可修改
- ✅ **余额查询**: `balanceOf` 返回账户的代币余额
- ✅ **转账机制**: `transfer` 直接转账，`transferFrom` 授权转账
- ✅ **授权机制**: `approve` 设置授权额度，`allowance` 查询授权额度
- ✅ **事件通知**: `Transfer` 和 `Approval` 事件记录转账和授权

---

### 2. 完整实现

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";

contract MyToken is ERC20, ERC20Burnable, Ownable {
    constructor(
        string memory name,
        string memory symbol,
        uint256 initialSupply
    ) ERC20(name, symbol) Ownable(msg.sender) {
        // 铸造初始供应量给部署者
        _mint(msg.sender, initialSupply * 10 ** decimals());
    }

    // ===================== 增发代币 =====================
    function mint(address to, uint256 amount) public onlyOwner {
        _mint(to, amount);
    }

    // ===================== 销毁代币 =====================
    function burn(uint256 amount) public override {
        super.burn(amount);
    }
}
```

**OpenZeppelin 特性**:
- ✅ **ERC20**: 基础代币功能（转账、授权、余额）
- ✅ **ERC20Burnable**: 可销毁代币（减少供应量）
- ✅ **Ownable**: 所有权管理（只有 owner 可以增发）

---

### 3. Gas 优化

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract GasOptimizedERC20 {
    // ===================== 使用 uint256 打包存储 =====================
    // 优化 1: 将多个小值打包到一个 slot
    struct PackedAccount {
        uint128 balance;  // 128 位
        uint128 allowance;  // 128 位
    }

    mapping(address => PackedAccount) private _accounts;

    // ===================== 使用 unchecked 块 =====================
    // 优化 2: 不检查溢出（已知不会溢出）
    function transfer(address recipient, uint256 amount) external returns (bool) {
        unchecked {
            _accounts[msg.sender].balance -= amount;
            _accounts[recipient].balance += amount;
        }
        return true;
    }

    // ===================== 使用 calldata 而不是 memory =====================
    // 优化 3: 避免复制到内存
    function batchTransfer(
        address[] calldata recipients,
        uint256[] calldata amounts
    ) external {
        require(recipients.length == amounts.length, "Length mismatch");

        unchecked {
            for (uint256 i = 0; i < recipients.length; ++i) {
                _accounts[msg.sender].balance -= amounts[i];
                _accounts[recipients[i]].balance += amounts[i];
            }
        }
    }
}
```

**Gas 优化技巧**:
- ✅ **打包存储**: 将多个小值打包到一个 256 位槽
- ✅ **使用 unchecked**: 算术运算不检查溢出
- ✅ **使用 calldata**: 避免复制到内存
- ✅ **减少 SLOAD/SSTORE**: 使用内存缓存

---

## 🎨 ERC-721: NFT 标准

### 1. 标准接口

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC721 {
    // ===================== 总量 =====================
    function balanceOf(address owner) external view returns (uint256);

    // ===================== 所有权 =====================
    function ownerOf(uint256 tokenId) external view returns (address);
    function transferFrom(address from, address to, uint256 tokenId) external;
    function safeTransferFrom(address from, address to, uint256 tokenId) external;
    function safeTransferFrom(address from, address to, uint256 tokenId, bytes calldata data) external;
    function approve(address to, uint256 tokenId) external;
    function setApprovalForAll(address operator, bool approved) external;
    function getApproved(uint256 tokenId) external view returns (address);
    function isApprovedForAll(address owner, address operator) external view returns (bool);

    // ===================== 事件 =====================
    event Transfer(address indexed from, address indexed to, uint256 indexed tokenId);
    event Approval(address indexed owner, address indexed approved, uint256 indexed tokenId);
    event ApprovalForAll(address indexed owner, address indexed operator, bool approved);
}
```

**与 ERC-20 的区别**:
- ✅ **不可替代性**: 每个 NFT 都是唯一的（tokenId 唯一）
- ✅ **元数据**: 每个 NFT 可以有不同的元数据（名称、描述、图片）
- ✅ **批量授权**: `setApprovalForAll` 授权所有 NFT 给 operator

---

### 2. 完整实现

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract MyNFT is ERC721, ERC721URIStorage, Ownable {
    using Counters for Counters.Counter;

    Counters.Counter private _tokenIdCounter;

    constructor() ERC721("MyNFT", "MNFT") Ownable(msg.sender) {}

    // ===================== 铸造 NFT =====================
    function mint(address to, string memory uri) public onlyOwner returns (uint256) {
        uint256 tokenId = _tokenIdCounter.current();
        _tokenIdCounter.increment();

        _safeMint(to, tokenId);
        _setTokenURI(tokenId, uri);

        return tokenId;
    }

    // ===================== 批量铸造 =====================
    function batchMint(address to, string[] memory uris) public onlyOwner {
        for (uint256 i = 0; i < uris.length; ++i) {
            uint256 tokenId = _tokenIdCounter.current();
            _tokenIdCounter.increment();

            _safeMint(to, tokenId);
            _setTokenURI(tokenId, uris[i]);
        }
    }

    // ===================== 重写函数 =====================
    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}
```

**OpenZeppelin 特性**:
- ✅ **ERC721**: 基础 NFT 功能（铸造、转账、授权）
- ✅ **ERC721URIStorage**: 元数据存储（tokenURI）
- ✅ **Ownable**: 所有权管理
- ✅ **Counters**: 安全的计数器（防止溢出）

---

### 3. 元数据标准 (ERC-721 Metadata)

```json
{
  "name": "My Awesome NFT #1",
  "description": "This is an awesome NFT!",
  "image": "https://example.com/nft/1.png",
  "attributes": [
    {
      "trait_type": "Background",
      "value": "Blue"
    },
    {
      "trait_type": "Rarity",
      "value": "Legendary"
    }
  ]
}
```

**元数据结构**:
- ✅ **name**: NFT 名称
- ✅ **description**: 描述
- ✅ **image**: 图片 URL
- ✅ **attributes**: 属性列表（trait_type + value）

---

## 🎯 ERC-1155: 多代币标准

### 1. 标准接口

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC1155 {
    // ===================== 批量查询 =====================
    function balanceOf(address account, uint256 id) external view returns (uint256);
    function balanceOfBatch(address[] calldata accounts, uint256[] calldata ids) external view returns (uint256[] memory);

    // ===================== 批量转账 =====================
    function safeTransferFrom(address from, address to, uint256 id, uint256 amount, bytes calldata data) external;
    function safeBatchTransferFrom(address from, address to, uint256[] calldata ids, uint256[] calldata amounts, bytes calldata data) external;

    // ===================== 事件 =====================
    event TransferSingle(address indexed operator, address indexed from, address indexed to, uint256 id, uint256 value);
    event TransferBatch(address indexed operator, address indexed from, address indexed to, uint256[] ids, uint256[] values);
    event ApprovalForAll(address indexed account, address indexed operator, bool approved);
    event URI(string value, uint256 indexed id);
}
```

**与 ERC-20 和 ERC-721 的区别**:
- ✅ **多代币**: 一个合约可以管理多个代币类型
- ✅ **批量操作**: 支持批量转账，节省 Gas
- ✅ **同质化和非同质化**: 支持同质化代币（如金币）和非同质化代币（如 NFT）

---

### 2. 完整实现

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC1155/extensions/ERC1155Supply.sol";

contract MyMultiToken is ERC1155, ERC1155Supply, Ownable {
    constructor(string memory uri) ERC1155(uri) Ownable(msg.sender) {}

    // ===================== 铸造代币 =====================
    function mint(address account, uint256 id, uint256 amount, bytes memory data) public onlyOwner {
        _mint(account, id, amount, data);
    }

    // ===================== 批量铸造 =====================
    function mintBatch(
        address to,
        uint256[] memory ids,
        uint256[] memory amounts,
        bytes memory data
    ) public onlyOwner {
        _mintBatch(to, ids, amounts, data);
    }

    // ===================== 更新 URI =====================
    function setURI(string memory newuri) public onlyOwner {
        _setURI(newuri);
    }

    // ===================== 重写函数 =====================
    function _update(address from, address to, uint256[] memory ids, uint256[] memory values)
        internal
        override(ERC1155, ERC1155Supply)
    {
        super._update(from, to, ids, values);
    }
}
```

**OpenZeppelin 特性**:
- ✅ **ERC1155**: 基础多代币功能
- ✅ **ERC1155Supply**: 供应量管理（可查询每个代币类型的总供应量）
- ✅ **Ownable**: 所有权管理

---

### 3. 批量转账示例

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract BatchTransfer {
    IERC1155 public token;

    constructor(address tokenAddress) {
        token = IERC1155(tokenAddress);
    }

    // ===================== 批量转账 =====================
    function batchTransfer(
        address[] calldata recipients,
        uint256[] calldata tokenIds,
        uint256[] calldata amounts
    ) external {
        require(recipients.length == tokenIds.length, "Length mismatch");
        require(tokenIds.length == amounts.length, "Length mismatch");

        unchecked {
            for (uint256 i = 0; i < recipients.length; ++i) {
                token.safeTransferFrom(
                    msg.sender,
                    recipients[i],
                    tokenIds[i],
                    amounts[i],
                    ""
                );
            }
        }
    }
}
```

**批量转账的优势**:
- ✅ **Gas 节省**: 一次交易完成多个转账，节省 20-30% 的 Gas
- ✅ **原子性**: 要么全部成功，要么全部失败
- ✅ **简洁性**: 减少交易数量

---

## 🏦 ERC-4626: 代币化金库标准

### 1. 标准接口

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC4626 {
    // ===================== 金库信息 =====================
    function asset() external view returns (address);
    function totalAssets() external view returns (uint256);

    // ===================== 转换比例 =====================
    function convertToShares(uint256 assets) external view returns (uint256);
    function convertToAssets(uint256 shares) external view returns (uint256);
    function maxDeposit(address) external view returns (uint256);
    function maxMint(address) external view returns (uint256);
    function maxWithdraw(address) external view returns (uint256);
    function maxRedeem(address owner) external view returns (uint256);

    // ===================== 存款 =====================
    function previewDeposit(uint256 assets) external view returns (uint256);
    function deposit(uint256 assets, address receiver) external returns (uint256);
    function mint(uint256 shares, address receiver) external returns (uint256);

    // ===================== 取款 =====================
    function previewWithdraw(uint256 assets) external view returns (uint256);
    function withdraw(uint256 assets, address receiver, address owner) external returns (uint256);
    function previewRedeem(uint256 shares) external view returns (uint256);
    function redeem(uint256 shares, address receiver, address owner) external returns (uint256);
}
```

**设计原理**:
- ✅ **资产金库**: 用户存入资产（如 USDC），获得金库份额
- ✅ **流动性**: 金库可以将资产借贷给其他用户，赚取收益
- ✅ **标准化**: 所有金库使用相同的接口，易于集成

---

### 2. 完整实现

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/token/ERC721/utils/ERC721Holder.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract MyVault is Ownable, ERC721Holder {
    using SafeERC20 for IERC20;

    IERC20 public immutable assetToken;
    IERC721 public immutable nftToken;

    // ===================== 金库状态 =====================
    uint256 public totalAssets;
    mapping(address => uint256) public userAssets;
    mapping(address => uint256) public userNFTs;

    // ===================== 事件 =====================
    event Deposit(address indexed user, uint256 assets);
    event Withdraw(address indexed user, uint256 assets);
    event DepositNFT(address indexed user, uint256 tokenId);
    event WithdrawNFT(address indexed user, uint256 tokenId);

    // ===================== 构造函数 =====================
    constructor(address assetToken_, address nftToken_) Ownable(msg.sender) {
        assetToken = IERC20(assetToken_);
        nftToken = IERC721(nftToken_);
    }

    // ===================== 存款 =====================
    function deposit(uint256 amount) external {
        require(amount > 0, "Amount must be > 0");

        // 转入资产
        assetToken.safeTransferFrom(msg.sender, address(this), amount);

        // 更新状态
        userAssets[msg.sender] += amount;
        totalAssets += amount;

        emit Deposit(msg.sender, amount);
    }

    // ===================== 取款 =====================
    function withdraw(uint256 amount) external {
        require(amount > 0, "Amount must be > 0");
        require(userAssets[msg.sender] >= amount, "Insufficient balance");

        // 更新状态
        userAssets[msg.sender] -= amount;
        totalAssets -= amount;

        // 转出资产
        assetToken.safeTransfer(msg.sender, amount);

        emit Withdraw(msg.sender, amount);
    }

    // ===================== 存款 NFT =====================
    function depositNFT(uint256 tokenId) external {
        // 转入 NFT
        nftToken.safeTransferFrom(msg.sender, address(this), tokenId);

        // 更新状态
        userNFTs[msg.sender] += 1;

        emit DepositNFT(msg.sender, tokenId);
    }

    // ===================== 取出 NFT =====================
    function withdrawNFT(uint256 tokenId) external {
        require(userNFTs[msg.sender] > 0, "No NFTs deposited");

        // 更新状态
        userNFTs[msg.sender] -= 1;

        // 转出 NFT
        nftToken.safeTransferFrom(address(this), msg.sender, tokenId);

        emit WithdrawNFT(msg.sender, tokenId);
    }

    // ===================== 查询余额 =====================
    function balanceOf(address user) external view returns (uint256) {
        return userAssets[user];
    }

    function nftBalanceOf(address user) external view returns (uint256) {
        return userNFTs[user];
    }
}
```

**金库功能**:
- ✅ **资产存款**: 存入 ERC20 代币（如 USDC）
- ✅ **NFT 存款**: 存入 ERC721 代币（如 NFT）
- ✅ **取款**: 取出资产和 NFT
- ✅ **余额查询**: 查询用户余额

---

## 🏠 ERC-4907: 租赁 NFT 标准

### 1. 标准接口

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC4907 {
    // ===================== 租赁信息 =====================
    function setUser(uint256 tokenId, address user, uint64 expires) external;
    function userOf(uint256 tokenId) external view returns (address);

    // ===================== 事件 =====================
    event UpdateUser(uint256 indexed tokenId, address indexed user, uint64 expires);
}
```

**设计原理**:
- ✅ **所有权与使用权分离**: NFT 的 owner 拥有所有权，user 拥有使用权
- ✅ **过期时间**: 用户使用权的过期时间
- ✅ **租赁场景**: 适合游戏道具租赁、房地产租赁等

---

### 2. 完整实现

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract RentalNFT is ERC721, ERC721URIStorage, Ownable {
    using Counters for Counters.Counter;

    Counters.Counter private _tokenIdCounter;

    // ===================== 租赁信息 =====================
    struct UserInfo {
        address user;      // 用户地址
        uint64 expires;    // 过期时间（Unix 时间戳）
    }

    mapping(uint256 => UserInfo) private _users;

    // ===================== 事件 =====================
    event UpdateUser(uint256 indexed tokenId, address indexed user, uint64 expires);

    // ===================== 构造函数 =====================
    constructor() ERC721("RentalNFT", "RNFT") Ownable(msg.sender) {}

    // ===================== 铸造 NFT =====================
    function mint(address to, string memory uri) public onlyOwner returns (uint256) {
        uint256 tokenId = _tokenIdCounter.current();
        _tokenIdCounter.increment();

        _safeMint(to, tokenId);
        _setTokenURI(tokenId, uri);

        return tokenId;
    }

    // ===================== 设置用户 =====================
    function setUser(uint256 tokenId, address user, uint64 expires) external {
        require(_isApprovedOrOwner(msg.sender, tokenId), "Not approved or owner");

        _users[tokenId] = UserInfo({
            user: user,
            expires: expires
        });

        emit UpdateUser(tokenId, user, expires);
    }

    // ===================== 查询用户 =====================
    function userOf(uint256 tokenId) external view returns (address) {
        UserInfo storage info = _users[tokenId];
        if (info.user == address(0)) {
            return address(0);
        }

        // 检查是否过期
        if (block.timestamp > info.expires) {
            return address(0);
        }

        return info.user;
    }

    // ===================== 查询过期时间 =====================
    function userExpires(uint256 tokenId) external view returns (uint256) {
        return _users[tokenId].expires;
    }

    // ===================== 重写函数 =====================
    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}
```

**租赁功能**:
- ✅ **设置用户**: owner 可以设置 user 和过期时间
- ✅ **查询用户**: 查询当前 user（如果未过期）
- ✅ **自动过期**: 过期后 user 自动失效

---

## 🔄 OpenZeppelin 合约模板

### 1. 访问控制

#### Ownable

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";

contract MyContract is Ownable {
    constructor() Ownable(msg.sender) {}

    // ===================== 只有 owner 可以调用 =====================
    function ownerOnlyFunction() external onlyOwner {
        // 只有 owner 可以执行
    }

    // ===================== 转移所有权 =====================
    function transferOwnership(address newOwner) external onlyOwner {
        _transferOwnership(newOwner);
    }
}
```

**Ownable 特性**:
- ✅ **onlyOwner 修饰符**: 限制函数只能由 owner 调用
- ✅ **所有权转移**: 可以转移所有权给新地址
- ✅ **放弃所有权**: 可以放弃所有权（成为零地址）

---

#### AccessControl

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";

contract MyContract is AccessControl {
    // ===================== 定义角色 =====================
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant USER_ROLE = keccak256("USER_ROLE");

    constructor() {
        // 部署者默认为 ADMIN_ROLE
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
    }

    // ===================== 只有 ADMIN 可以调用 =====================
    function adminFunction() external onlyRole(ADMIN_ROLE) {
        // 只有 ADMIN 可以执行
    }

    // ===================== 任何 USER 都可以调用 =====================
    function userFunction() external onlyRole(USER_ROLE) {
        // 任何 USER 都可以执行
    }

    // ===================== 授予角色 =====================
    function grantRole(bytes32 role, address account) external onlyRole(DEFAULT_ADMIN_ROLE) {
        _grantRole(role, account);
    }

    // ===================== 撤销角色 =====================
    function revokeRole(bytes32 role, address account) external onlyRole(DEFAULT_ADMIN_ROLE) {
        _revokeRole(role, account);
    }
}
```

**AccessControl 特性**:
- ✅ **角色系统**: 支持多个角色（如 ADMIN、USER）
- ✅ **onlyRole 修饰符**: 限制函数只能由特定角色调用
- ✅ **角色继承**: DEFAULT_ADMIN_ROLE 可以授予和撤销其他角色

---

### 2. 安全合约

#### ReentrancyGuard

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract Vault is ReentrancyGuard {
    IERC20 public token;

    mapping(address => uint256) public balances;

    constructor(address tokenAddress) {
        token = IERC20(tokenAddress);
    }

    // ===================== 存款 =====================
    function deposit(uint256 amount) external {
        token.transferFrom(msg.sender, address(this), amount);
        balances[msg.sender] += amount;
    }

    // ===================== 取款（防止重入）=====================
    function withdraw(uint256 amount) external nonReentrant {
        require(balances[msg.sender] >= amount, "Insufficient balance");

        // 先更新状态，再转账
        balances[msg.sender] -= amount;

        token.transfer(msg.sender, amount);
    }
}
```

**ReentrancyGuard 特性**:
- ✅ **nonReentrant 修饰符**: 防止重入攻击
- ✅ **状态更新**: 先更新状态，再执行外部调用

---

#### Pausable

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/utils/Pausable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract MyPausableContract is Pausable, Ownable {
    constructor() Ownable(msg.sender) {}

    // ===================== 只有未暂停时可以调用 =====================
    function normalFunction() external whenNotPaused {
        // 只有未暂停时可以执行
    }

    // ===================== 只有暂停时可以调用 =====================
    function emergencyFunction() external whenPaused {
        // 只有暂停时可以执行
    }

    // ===================== 暂停合约 =====================
    function pause() external onlyOwner {
        _pause();
    }

    // ===================== 恢复合约 =====================
    function unpause() external onlyOwner {
        _unpause();
    }
}
```

**Pausable 特性**:
- ✅ **whenNotPaused 修饰符**: 只有未暂停时可以调用
- ✅ **whenPaused 修饰符**: 只有暂停时可以调用
- ✅ **紧急情况**: 可以在紧急情况下暂停合约

---

### 3. 代币扩展

#### ERC20Burnable

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";

contract BurnableToken is ERC20, ERC20Burnable {
    constructor(string memory name, string memory symbol) ERC20(name, symbol) {}

    function mint(address to, uint256 amount) external {
        _mint(to, amount);
    }

    // ===================== 销毁代币 =====================
    function burn(uint256 amount) public override {
        super.burn(amount);
    }

    // ===================== 销毁其他人的代币（需要授权）=====================
    function burnFrom(address account, uint256 amount) public override {
        super.burnFrom(account, amount);
    }
}
```

**ERC20Burnable 特性**:
- ✅ **burn**: 销毁自己的代币
- ✅ **burnFrom**: 销毁其他人的代币（需要授权）

---

#### ERC20Snapshot

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Snapshot.sol";

contract SnapshotToken is ERC20, ERC20Snapshot {
    uint256 private _snapshotId;

    constructor(string memory name, string memory symbol) ERC20(name, symbol) {}

    // ===================== 创建快照 =====================
    function snapshot() external returns (uint256) {
        _snapshotId = _snapshot();
        return _snapshotId;
    }

    // ===================== 查询历史余额 =====================
    function balanceOfAt(address account, uint256 snapshotId) external view returns (uint256) {
        return balanceOfAt(account, snapshotId);
    }

    // ===================== 查询历史总量 =====================
    function totalSupplyAt(uint256 snapshotId) external view returns (uint256) {
        return totalSupplyAt(snapshotId);
    }

    // ===================== 重写函数 =====================
    function _update(address from, address to, uint256 value)
        internal
        override(ERC20, ERC20Snapshot)
    {
        super._update(from, to, value);
    }
}
```

**ERC20Snapshot 特性**:
- ✅ **快照**: 在某个时间点记录所有账户的余额
- ✅ **历史查询**: 可以查询历史余额和总量
- ✅ **空投**: 可以根据快照进行空投

---

## 📊 EIP 对比表

| EIP | 类型 | 描述 | 使用场景 |
|-----|------|------|----------|
| **ERC-20** | Token | 同质化代币 | USDT、USDC、DeFi 治理代币 |
| **ERC-721** | Token | 非同质化代币 | NFT、游戏道具、艺术品 |
| **ERC-1155** | Token | 多代币标准 | 游戏道具、资产组合 |
| **ERC-4626** | Token | 代币化金库 | DeFi 收益金库 |
| **ERC-4907** | Token | 租赁 NFT | 游戏道具租赁、房地产租赁 |

---

## 🎯 实践练习

### 练习 1: 实现完整的 ERC-20 代币
- 支持铸造、销毁、批量转账
- 使用 OpenZeppelin 库
- 优化 Gas 消耗

### 练习 2: 实现 NFT 市场
- 支持 NFT 铸造、上架、购买
- 使用 ERC-721 标准
- 添加元数据存储

### 练习 3: 实现租赁 NFT
- 使用 ERC-4907 标准
- 支持租赁、续租、归还
- 添加过期时间管理

### 练习 4: 实现收益金库
- 使用 ERC-4626 标准
- 支持存款、取款、收益分配
- 添加风险控制

---

## 📚 学习资源

### 推荐阅读

1. **OpenZeppelin 官方文档** - contracts.openzeppelin.com
2. **EIP 官方仓库** - github.com/ethereum/EIPs
3. **Ethereum Improvement Proposals** - eips.ethereum.org

### 在线资源

- [OpenZeppelin Docs](https://docs.openzeppelin.com/contracts)
- [EIPs GitHub](https://github.com/ethereum/EIPs)
- [ERC-20 Explained](https://eips.ethereum.org/EIPS/eip-20)
- [ERC-721 Explained](https://eips.ethereum.org/EIPS/eip-721)

---

## 🚀 下一步

**完成度**: EIP 标准和 OpenZeppelin 研究 ✅

**下一步**: 继续其他研究方向或实践开发

---

**正在准备下一个主题...** 🧠
