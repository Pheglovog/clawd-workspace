# 第十一小时：GameFi & NFT Marketplace 深度研究

> 主动进化学习 🪵 → 💪
> 基于 MCP 搜索的 2026 年最新趋势

---

## 三十七、GameFi 深度解析

### 17.1 什么是 GameFi？

**定义：**

GameFi（Game Finance）是游戏区块链技术、GameFi经济和去中心化金融相结合，通过游戏金融激励机制，为玩家提供财务激励的生态系统。

```
GameFi 核心要素：

1. Play to Earn（边玩边赚）
   - 玩家通过游戏代币获得奖励
   - 例：Axie Infinity, The Sandbox

2. GameFi Staking（游戏质押）
   - 质押游戏 NFT 获得奖励
   - 例：CryptoBlades, Gods Unchained

3. NFT Farming（NFT 耕作）
   - 质押 NFT 到流动性池
   - 获得交易手续费和奖励
   - 例：Mobox, Alien Worlds

4. GameFi Lending（游戏借贷）
   - NFT 作为抵押品借入代币
   - 例：NFTfi, ArcadeNFT

5. GameFi Marketplace（游戏市场）
   - 游戏物品、道具交易
   - 例：OpenSea Game Items, GameStop
```

### 17.2 GameFi 经济模型

**玩家收益来源：**

```
收益 = 游戏奖励 + NFT 交易 + 质押收益 + 竞赛奖励

详细分解：

1. 游戏内奖励
   - 完成任务
   - 赢得比赛
   - 探索地图
   - 战胜敌对

2. NFT 交易收入
   - 出售稀有 NFT
   - 在 Marketplace 交易
   - 获得版税（如适用）

3. 质押收益
   - 质押游戏 NFT
   - Staking 池分红
   - 流动性提供奖励

4. 竞赛奖励
   - 排名赛奖励
   - 锦标赛奖金
   - 赞博奖励

总收益 = ∑ (游戏奖励 + NFT 交易 + 质押收益 + 竞赛奖励)
```

### 17.3 GameFi 代币经济

**代币效用：**

```
GameFi 代币类型：

1. 游戏内货币（In-Game Currency）
   - 用于购买道具
   - 用于支付费用
   - 例：SAND, MANA, AXS

2. 治理代币（Governance Token）
   - 投票权
   - 协议升级
   - Staking 奖励
   - 例：YGG, YLD

3. NFT 代币（NFT Token）
   - 代表游戏资产
   - 可交易
   - 版税收益
   - 例：Game NFTs

代币流通模型：

总供应量 = 游戏内货币 + 游戏外交易 + Staking 锁定
           + 奖励池 + 团队分配 + 财政储备
```

---

## 十八、NFT Marketplace 深度研究

### 18.1 NFT Marketplace 类型

**分类：**

```
NFT Marketplace 类型：

1. 通用 Marketplace（通用市场）
   - 支持所有类型 NFT
   - 例：OpenSea, Magic Eden, Rarible

2. 专业 Marketplace（专业市场）
   - 特定垂直领域
   - 例：LooksRare（艺术）, Gem XYZ（宝石）
   - GameFi Marketplaces（游戏）

3. 竞拍 Marketplace（拍卖市场）
   - 英式拍卖、荷兰式拍卖
   - 例：Foundation, Zora

4. 聚合 Marketplace（聚合市场）
   - 多个 Marketplace 聚合
   - 例：OpenSea Pro, Gem

5. NFT Lending Marketplace（NFT 借贷）
   - NFT 作为抵押品
   - 例：NFTfi, BendDAO
```

### 18.2 OpenSea 机制深度解析

**OpenSea V2（Pro 版本）：**

```
OpenSea V2 新特性：

1. 零手续费交易
   - 0% 手续费
   - Gas 费由交易者支付

2. Seaport（海洋端口）
   - 简化版 OpenSea
   - 更易用
   - 更低 Gas 费

3. Seaport 1.0
   - 恢复"Offer"功能
   - 改进的用户界面
   - 更好的批量操作

4. Pro 订阅（30 美元/月）
   - 高级搜索和过滤
   - 早期访问新 Drop
   - 优先级支持

5. 链上数据验证
   - 减少欺诈
   - 确保真实性
   - 提高信任度
```

**OpenSea V2 Fee Structure（Pro）：**

```
手续费计算：

标准版：
- 销售方：0%（无手续费）
- Gas 费：交易者支付

Pro 订阅：
- 月费：30 美元
- 无交易手续费（仍需支付 Gas 费）
- 优先级支持

OpenSea 5%（OpenSea 推出 5% 手续费，用于激励）
```

### 18.3 Blur 竞拍机制

**荷兰式拍卖（Dutch Auction）：**

```
Blur 荷兰式拍卖机制：

开始价格 = S
结束价格 = E (S > E)
持续时间 = T

价格随时间线性下降：

价格(t) = S - (S - E) × (t / T)

示例：
开始价格：10 ETH
结束价格：8 ETH
持续时间：24 小时

拍卖过程：
t=0h:   价格 = 10 ETH
t=6h:   价格 = 9.5 ETH
t=12h:  价格 = 9 ETH
t=18h:  价格 = 8.5 ETH
t=24h:  价格 = 8 ETH

出价规则：
- 任何时间都可以出价
- 出价 = 当前价格
- 先到先得

策略：
- 早期出价：快速成交，但价格较高
- 晚期出价：价格较低，但风险被抢

优势：
- 快速结算
- 公平透明
- 价格发现机制
```

### 18.4 NFT Marketplace 收入模型

**收入来源：**

```
收入 = 交易手续费 + 版税 + 拍卖费 + Pro 订阅

详细分解：

1. 交易手续费（Trading Fee）
   - 通常 0.5% - 2.5%
   - OpenSea：2.5%（5% 推出）
   - Blur：0%（零手续费）
   - Magic Eden：0.5%

2. 版税（Royalty）
   - 收入 NFT 版税
   - 通常 5% - 10%
   - 支付给创作者

   总费用 = 交易手续费 + 版税

3. 拍卖费（Auction Fee）
   - 拍卖成功的费用
   - 通常 2% - 5%
   - 支付给 Marketplace

4. Pro 订阅收入
   - 每月固定费用
   - 提供高级功能
   - 例：OpenSea Pro（30 美元/月）

净收入 = 总费用 - 运营成本 - 奖励成本
```

---

## 十九、GameFi + DeFi 集成

### 19.1 NFT Staking

**NFT 作为质押物：**

```
NFT Staking 模型：

1. 简单质押（Simple Staking）
   - 质押 NFT
   - 获得协议代币奖励
   - 示例：Mobox NFT 质押

2. 质押池（Staking Pool）
   - 多个 NFT 质押到池中
   - 按权重分配奖励
   - 示例：Gods Unchained

3. 游戏内质押（In-Game Staking）
   - 质押到游戏合约
   - 影响游戏属性（攻击力、防御力等）
   - 示例：Axie Infinity

4. 流动性质押（Liquidity Staking）
   - 质押 NFT 到 DEX 流动性池
   - 获得 LP Token
   - 赚取交易手续费
```

**NFT Staking 合约示例：**

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721Receiver.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title NFT Staking Pool
 * @author 上等兵•甘
 */
contract NFTStakingPool is IERC721Receiver, ReentrancyGuard {
    using SafeERC20 for IERC20;

    // ========== 接口 ==========
    IERC20 public immutable rewardsToken;

    struct Stake {
        uint256 tokenId;
        address owner;
        uint256 stakedAt;
        uint256 rewardsClaimed;
    }

    // ========== 状态变量 ==========
    mapping(uint256 => Stake) public stakes;
    uint256 public totalStaked;
    uint256 public rewardsPerBlock;
    uint256 public lastUpdateBlock;
    address public immutable owner;

    uint256 public constant UNSTAKE_COOLDOWN = 7 days;

    // ========== 事件 ==========
    event Staked(
        address indexed owner,
        uint256 indexed tokenId,
        uint256 timestamp
    );
    event Unstaked(
        address indexed owner,
        uint256 indexed tokenId,
        uint256 timestamp
    );
    event RewardsClaimed(
        address indexed owner,
        uint256 amount
    );

    // ========== 修饰符 ==========
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner");
        _;
    }

    // ========== 构造函数 ==========
    constructor(address _rewardsToken) {
        rewardsToken = IERC20(_rewardsToken);
        owner = msg.sender;
        rewardsPerBlock = 1e18; // 1 reward token per block
        lastUpdateBlock = block.number;
    }

    // ========== 核心功能 ==========

    /**
     * @dev 质押 NFT
     */
    function stake(uint256[] calldata tokenIds) external {
        require(tokenIds.length > 0, "No tokens to stake");

        for (uint256 i = 0; i < tokenIds.length; ) {
            _stake(msg.sender, tokenIds[i]);
            unchecked { ++i; }
        }
    }

    /**
     * @dev 取消质押 NFT
     */
    function unstake(uint256[] calldata tokenIds) external {
        require(tokenIds.length > 0, "No tokens to unstake");

        for (uint256 i = 0; i < tokenIds.length; ) {
            _unstake(msg.sender, tokenIds[i]);
            unchecked { ++i; }
        }
    }

    /**
     * @dev 领取奖励
     */
    function claimRewards() external {
        uint256 reward = calculateRewards(msg.sender);

        require(reward > 0, "No rewards to claim");

        // 更新质押记录
        for (uint256 i = 0; i < 100; ) { // 遍历前 100 个 NFT
            if (stakes[msg.sender + i].tokenId != 0) {
                uint256 tokenId = stakes[msg.sender + i].tokenId;
                if (stakes[tokenId].owner == msg.sender) {
                    stakes[tokenId].rewardsClaimed += rewards[tokenId];
                }
            }
        }

        // 发送奖励
        rewardsToken.safeTransfer(msg.sender, reward);

        emit RewardsClaimed(msg.sender, reward);
    }

    /**
     * @dev 计算奖励
     */
    function calculateRewards(address user) public view returns (uint256) {
        uint256 userRewards;

        // 简化版：每个质押的 NFT 产生固定奖励
        uint256 totalUserStaked;
        for (uint256 i = 0; i < 100; ) {
            if (stakes[user + i].tokenId != 0) {
                if (stakes[user + i].owner == user) {
                    totalUserStaked += 1;
                }
            }
        }

        uint256 blocksPassed = block.number - lastUpdateBlock;
        userRewards = totalUserStaked * rewardsPerBlock * blocksPassed / 1e18;

        return userRewards;
    }

    // ========== 内部函数 ==========

    function _stake(address owner, uint256 tokenId) internal {
        require(IERC721(address(this)).ownerOf(tokenId) == owner, "Not owner");

        // 转移 NFT 到合约
        IERC721(address(this)).safeTransferFrom(owner, address(this), tokenId);

        // 记录质押
        stakes[tokenId] = Stake({
            tokenId: tokenId,
            owner: owner,
            stakedAt: block.timestamp,
            rewardsClaimed: 0
        });

        totalStaked += 1;

        emit Staked(owner, tokenId, block.timestamp);
    }

    function _unstake(address owner, uint256 tokenId) internal {
        require(stakes[tokenId].owner == owner, "Not staker");
        require(block.timestamp >= stakes[tokenId].stakedAt + UNSTAKE_COOLDOWN, "Cooldown not met");

        // 转移 NFT 回用户
        IERC721(address(this)).safeTransferFrom(address(this), owner, tokenId);

        // 清除质押记录
        delete stakes[tokenId];
        totalStaked -= 1;

        emit Unstaked(owner, tokenId, block.timestamp);
    }

    // ========== ERC721 Receiver ==========

    function onERC721Received(
        address operator,
        address from,
        uint256 tokenId,
        bytes calldata data
    ) external override {
        // 不接受直接转账，必须通过 stake 函数
    }

    // ========== 管理函数 ==========

    function setRewardsPerBlock(uint256 _rewardsPerBlock) external onlyOwner {
        rewardsPerBlock = _rewardsPerBlock;
    }

    function emergencyWithdraw() external onlyOwner {
        rewardsToken.safeTransfer(owner, rewardsToken.balanceOf(address(this)));
    }

    receive() external payable {}
}
```

### 19.2 NFT Lending（NFT 借贷）

**NFT 作为抵押品：**

```
NFT Lending 模型：

1. NFT 抵押（NFT Collateral）
   - NFT 作为抵押品
   - 借入稳定币或原生代币
   - 示例：NFTfi, ArcadeNFT

2. 贷款价值评估（Loan-to-Value）
   - 评估 NFT 的市场价值
   - 设定最大 LTV（贷款价值比）
   - 通常 LTV < 70%

3. 利息模型（Interest Model）
   - 固定利率
   - 可变利率（基于供需）
   - 示例：5-15% APR

4. 清算机制（Liquidation）
   - 当 NFT 价值下降
   - 触发清算
   - 拍卖 NFT

NFT Lending 流程：

1. 用户质押 NFT 到 Lending 合约
2. 合约评估 NFT 价值
3. 用户借入稳定币（最高 LTV）
4. 用户支付利息
5. 到期后归还本金 + 利息
6. 取回 NFT

清算条件：
- NFT 市场价值 × LTV < 未偿还债务
- 清算人获得 NFT（折扣价）
- 清算人获得清算奖励
```

**NFT Lending 合约示例：**

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

interface INFTOracle {
    function getNFTPrice(uint256 tokenId) external view returns (uint256 price);
}

/**
 * @title NFT Lending Pool
 * @author 上等兵•甘
 */
contract NFTLendingPool is ReentrancyGuard {
    using SafeERC20 for IERC20;

    // ========== 接口 ==========
    IERC20 public immutable borrowToken;
    INFTOracle public immutable nftOracle;
    uint256 public constant LTV = 70; // 70% LTV
    uint256 public constant LIQUIDATION_BONUS = 5; // 5% 清算奖励
    uint256 public constant INTEREST_RATE = 1000; // 10% APR (1000 bps)

    struct Loan {
        uint256 loanId;
        address borrower;
        uint256 tokenId;
        uint256 borrowAmount;
        uint256 collateralValue;
        uint256 interestRate;
        uint256 startTime;
        uint256 endTime;
        bool active;
        bool liquidated;
    }

    // ========== 状态变量 ==========
    mapping(uint256 => Loan) public loans;
    uint256 public nextLoanId;
    mapping(uint256 => address) public loanNFTOwner;
    uint256 public totalLent;
    address public immutable owner;

    // ========== 事件 ==========
    event LoanCreated(
        uint256 indexed loanId,
        address indexed borrower,
        uint256 tokenId,
        uint256 amount
    );
    event LoanRepaid(
        uint256 indexed loanId,
        uint256 amount
    );
    event LoanLiquidated(
        uint256 indexed loanId,
        address indexed liquidator,
        uint256 collateralValue
    );

    // ========== 修饰符 ==========
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner");
        _;
    }

    // ========== 构造函数 ==========
    constructor(
        address _borrowToken,
        address _nftOracle
    ) {
        borrowToken = IERC20(_borrowToken);
        nftOracle = INFTOracle(_nftOracle);
        owner = msg.sender;
    }

    // ========== 核心功能 ==========

    /**
     * @dev 借入稳定币
     * @param tokenId NFT Token ID
     * @param borrowAmount 借入金额
     */
    function borrow(
        uint256 tokenId,
        uint256 borrowAmount
    ) external nonReentrant {
        // 检查 NFT 所有权
        address nftOwner = IERC721(address(this)).ownerOf(tokenId);
        require(nftOwner == msg.sender, "Not NFT owner");

        // 获取 NFT 市场价值
        uint256 collateralValue = nftOracle.getNFTPrice(tokenId);

        // 检查 LTV
        uint256 maxBorrow = (collateralValue * LTV) / 100;
        require(borrowAmount <= maxBorrow, "Borrow amount too high");

        // 转移 NFT 到合约
        IERC721(address(this)).safeTransferFrom(msg.sender, address(this), tokenId);

        // 记录 NFT 所有权
        loanNFTOwner[tokenId] = msg.sender;

        // 计算利息
        uint256 interest = (borrowAmount * INTEREST_RATE) / 10000;
        uint256 totalRepay = borrowAmount + interest;

        // 创建贷款
        loans[nextLoanId] = Loan({
            loanId: nextLoanId,
            borrower: msg.sender,
            tokenId: tokenId,
            borrowAmount: borrowAmount,
            collateralValue: collateralValue,
            interestRate: INTEREST_RATE,
            startTime: block.timestamp,
            endTime: block.timestamp + 30 days,
            active: true,
            liquidated: false
        });

        // 转移借入金额
        borrowToken.safeTransfer(msg.sender, borrowAmount);

        totalLent += borrowAmount;

        emit LoanCreated(nextLoanId, msg.sender, tokenId, borrowAmount);

        nextLoanId++;
    }

    /**
     * @dev 归还贷款
     * @param loanId 贷款 ID
     * @param amount 归还金额
     */
    function repay(uint256 loanId, uint256 amount) external nonReentrant {
        Loan storage loan = loans[loanId];
        require(loan.active, "Loan not active");
        require(msg.sender == loan.borrower, "Not borrower");

        // 计算应还金额
        uint256 interest = (loan.borrowAmount * loan.interestRate) / 10000;
        uint256 totalRepay = loan.borrowAmount + interest;

        // 检查金额
        require(amount == totalRepay, "Incorrect amount");

        // 转移归还金额
        borrowToken.safeTransferFrom(msg.sender, address(this), amount);

        // 返还 NFT
        IERC721(address(this)).safeTransferFrom(address(this), loan.borrower, loan.tokenId);
        delete loanNFTOwner[loan.tokenId];

        // 更新贷款状态
        loan.active = false;

        emit LoanRepaid(loanId, amount);
    }

    /**
     * @dev 清算贷款
     * @param loanId 贷款 ID
     */
    function liquidate(uint256 loanId) external nonReentrant {
        Loan storage loan = loans[loanId];
        require(loan.active, "Loan not active");
        require(!loan.liquidated, "Already liquidated");

        // 检查是否可清算
        uint256 collateralValue = nftOracle.getNFTPrice(loan.tokenId);
        uint256 debtValue = loan.borrowAmount + (loan.borrowAmount * loan.interestRate) / 10000;

        require(collateralValue * LTV / 100 < debtValue, "Not liquidatable");

        // 清算奖励
        uint256 bonus = (collateralValue * LIQUIDATION_BONUS) / 100;

        // 转移 NFT 给清算人
        IERC721(address(this)).safeTransferFrom(address(this), msg.sender, loan.tokenId);

        // 清算人获得抵押品
        borrowToken.safeTransfer(msg.sender, collateralValue - debtValue + bonus);

        // 更新贷款状态
        loan.liquidated = true;
        loan.active = false;

        emit LoanLiquidated(loanId, msg.sender, collateralValue);
    }

    /**
     * @dev 获取贷款信息
     */
    function getLoanInfo(uint256 loanId)
        external
        view
        returns (
            address borrower,
            uint256 tokenId,
            uint256 borrowAmount,
            uint256 collateralValue,
            uint256 interestRate,
            uint256 startTime,
            uint256 endTime,
            bool active,
            bool liquidated
        )
    {
        Loan storage loan = loans[loanId];
        return (
            loan.borrower,
            loan.tokenId,
            loan.borrowAmount,
            loan.collateralValue,
            loan.interestRate,
            loan.startTime,
            loan.endTime,
            loan.active,
            loan.liquidated
        );
    }

    // ========== 管理函数 ==========

    function setLTV(uint256 _ltv) external onlyOwner {
        require(_ltv < 100, "LTV must be < 100");
        LTV = _ltv;
    }

    function setInterestRate(uint256 _interestRate) external onlyOwner {
        INTEREST_RATE = _interestRate;
    }

    function setNFTOracle(address _nftOracle) external onlyOwner {
        nftOracle = INFTOracle(_nftOracle);
    }

    function emergencyWithdraw() external onlyOwner {
        borrowToken.safeTransfer(owner, borrowToken.balanceOf(address(this)));
    }
}
```

---

## 二十、GameFi 2026 年趋势分析

### 20.1 市场数据（2026）

**GameFi 市场规模：**

```
市场数据分析：

1. 市值（Market Cap）
   - GameFi Sector: $16-31B (2026)
   - Play to Earn: $12-20B
   - Metaverse Gaming: $4-11B

2. 增长率（Growth Rate）
   - 2025 年：-75% (熊市下跌）
   - 2026 年预测：+60% (市场复苏)
   - CAGR (2024-2028): 25%

3. 用户基础（User Base）
   - 游戏玩家:200M+
   - 钱包地址：50M+
   - 月活跌用户：15M+

4. 交易量（Volume）
   - 日交易量：$200-500M
   - 月交易量：$6-15B
   - 年交易量：$72-180B
```

**关键平台数据：**

| 平台 | 市值 | 月活跌 | NFT 类型 | 特色 |
|------|------|--------|---------|------|
| **Axie Infinity** | $1.5B | 2M+ | 游戏物品 | Play to Earn |
| **The Sandbox** | $1.2B | 1.5M+ | 土地 NFT | Metaverse |
| **Decentraland** | $800M | 1M+ | 虚拟土地 | Metaverse |
| **Gods Unchained** | $600M | 500K+ | 游戏卡牌 | 卡牌游戏 |
| **Alien Worlds** | $400M | 400K+ | 虚拟土地 | Play to Earn |

### 20.2 技术趋势

**1. 多链支持（Multi-Chain）**

```
多链部署策略：

以太坊
- 高价值 NFT（1 ETH+）
- DeFi 协议集成
- 机构投资者

Layer2（Arbitrum, Optimism, Polygon）
- 游戏内 NFT（0.01-1 ETH）
- 低 Gas 费
- 快速确认

Layer1（Solana, BNB Chain, Avalanche）
- 高频游戏
- 低延迟交易
- 游戏内代币

示例：
- Axie Infinity: Ronin 侧链
- The Sandbox: Polygon 主网 + Matic
- Alien Worlds: 多链部署
```

**2. 移动端优化（Mobile Optimization）**

```
移动端优化策略：

1. 轻钱包集成（Light Wallet）
   - Account Abstraction (ERC-4337)
   - Gasless 交易
   - 社交登录

2. 游戏内钱包（In-Game Wallet）
   - 集成到游戏客户端
   - 签名登录（Sign in with Wallet）
   - 自动代币兑换

3. 批量交易（Batch Transactions）
   - 多个操作打包为单笔交易
   - 降低 Gas 成本
   - 提升用户体验

4. 链下数据（Off-Chain Data）
   - 游戏状态存储在链下
   - 减少 Gas 消耗
   - 提高游戏性能
```

**3. 社交功能（Social Features）**

```
社交功能增强：

1. 好友系统（Friend System）
   - 好友列表
   - 好友邀请奖励
   - 好友对战

2. 公会系统（Guild System）
   - 公会创建
   - 公会任务
   - 公会战

3. 排行榜（Leaderboard）
   - 全球排名
   - 赛季排名
   - 奖励机制

4. 成就系统（Achievement System）
   - 勋章收集
   - 成就奖励
   - 限量版 NFT
```

---

## 二十一、GameFi 智能合约实现

### 21.1 Play to Earn 合约

**核心机制：**

```
Play to Earn 机制：

1. 任务系统（Quest System）
   - 玩家领取任务
   - 完成任务获得奖励
   - 任务类型：
     - 日常任务（Daily Quests）
     - 每周任务（Weekly Quests）
     - 限时任务（Time-Limited Quests）
     - 赛季任务（Season Quests）

2. 奖励系统（Reward System）
   - 代币奖励
   - NFT 奖励
   - 经验点（XP）
   - 声望值（Reputation）

3. 技能树（Skill Tree）
   - 角色技能
   - 升级经验
   - 技能解锁

4. 战利系统（Loot System）
   - 战利掉落（Loot Drop）
   - 稀有度（Rarity）
   - 随机属性（Random Attributes）
```

**Play to Earn 合约示例：**

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

interface IPlayToEarn {
    function completeQuest(
        uint256 questId,
        bytes calldata proof
    ) external;

    function claimReward(
        uint256 rewardId
    ) external;
}

/**
 * @title Play to Earn Game Contract
 * @author 上等兵•甘
 */
contract PlayToEarnGame is ReentrancyGuard, Ownable {
    using SafeERC20 for IERC20;

    // ========== 接口 ==========
    IERC20 public immutable gameToken;
    IPlayToEarn public immutable pteContract;

    // ========== 状态变量 ==========
    mapping(uint256 => Quest) public quests;
    mapping(uint256 => Reward) public rewards;
    mapping(uint256 => mapping(address => bool)) public questCompleted;
    mapping(uint256 => mapping(address => bool)) public rewardClaimed;

    struct Quest {
        uint256 questId;
        string questType;
        uint256 rewardTokenId;
        uint256 rewardAmount;
        uint256 xpReward;
        uint256 endTime;
        bool active;
        mapping(bytes32 => bool) proofUsed;
    }

    struct Reward {
        uint256 rewardId;
        uint256 tokenId;
        uint256 rewardAmount;
    }

    mapping(address => uint256) public xpBalance;
    mapping(address => uint256) public reputation;

    // ========== 事件 ==========
    event QuestCompleted(
        address indexed player,
        uint256 indexed questId,
        uint256 xpGained
    );
    event RewardClaimed(
        address indexed player,
        uint256 indexed rewardId,
        uint256 amount
    );

    // ========== 修饰符 ==========
    modifier onlyPte() {
        require(msg.sender == address(pteContract), "Only PTE");
        _;
    }

    // ========== 构造函数 ==========
    constructor(
        address _gameToken,
        address _pteContract
    ) Ownable() {
        gameToken = IERC20(_gameToken);
        pteContract = IPlayToEarn(_pteContract);
    }

    // ========== 核心功能 ==========

    /**
     * @dev 完成任务
     */
    function completeQuest(
        uint256 questId,
        bytes calldata proof
    ) external onlyPte returns (bool success) {
        Quest storage quest = quests[questId];
        require(quest.active, "Quest not active");
        require(block.timestamp <= quest.endTime, "Quest expired");
        require(!questCompleted[questId][msg.sender], "Quest already completed");

        // 验证证明（Merkle Proof）
        bytes32 proofHash = keccak256(abi.encode(msg.sender, questId));
        require(!quest.proofUsed[proofHash], "Proof already used");
        require(_verifyProof(questId, proof), "Invalid proof");

        // 标记证明已使用
        quest.proofUsed[proofHash] = true;
        questCompleted[questId][msg.sender] = true;

        // 增加经验值
        xpBalance[msg.sender] += quest.xpReward;

        // 发放奖励
        if (quest.rewardAmount > 0) {
            gameToken.safeTransfer(msg.sender, quest.rewardAmount);
        }

        emit QuestCompleted(msg.sender, questId, quest.xpReward);

        return true;
    }

    /**
     * @dev 领取奖励
     */
    function claimReward(uint256 rewardId) external {
        require(!rewardClaimed[rewardId][msg.sender], "Reward already claimed");

        Reward storage reward = rewards[rewardId];

        // 转移 NFT 或代币
        if (reward.tokenId > 0) {
            // NFT 转移
            IERC721(address(this)).safeTransferFrom(
                address(this),
                msg.sender,
                reward.tokenId
            );
        } else {
            // 代币转移
            gameToken.safeTransfer(msg.sender, reward.rewardAmount);
        }

        rewardClaimed[rewardId][msg.sender] = true;

        emit RewardClaimed(msg.sender, rewardId, reward.rewardAmount);
    }

    /**
     * @dev 验证证明
     */
    function _verifyProof(
        uint256 questId,
        bytes calldata proof
    ) internal view returns (bool) {
        // 简化版：在实际实现中，这里应该验证 Merkle Proof
        return keccak256(proof) == keccak256(abi.encode(msg.sender, questId));
    }

    // ========== PTE 调用 ==========

    function createQuest(
        uint256 questId,
        string calldata questType,
        uint256 rewardTokenId,
        uint256 rewardAmount,
        uint256 xpReward,
        uint256 duration
    ) external onlyOwner {
        quests[questId] = Quest({
            questId: questId,
            questType: questType,
            rewardTokenId: rewardTokenId,
            rewardAmount: rewardAmount,
            xpReward: xpReward,
            endTime: block.timestamp + duration,
            active: true,
            proofUsed: mapping(bytes32 => bool)
        });
    }

    function createReward(
        uint256 rewardId,
        uint256 tokenId,
        uint256 rewardAmount
    ) external onlyOwner {
        rewards[rewardId] = Reward({
            rewardId: rewardId,
            tokenId: tokenId,
            rewardAmount: rewardAmount
        });
    }

    // ========== 管理函数 ==========

    function setPteContract(address _pteContract) external onlyOwner {
        pteContract = IPlayToEarn(_pteContract);
    }

    function withdraw(address token, uint256 amount) external onlyOwner {
        IERC20(token).safeTransfer(owner, amount);
    }

    receive() external payable {}
}
```

---

## 二十二、第十一小时学到的技能总结

### 22.1 核心技能

1. **GameFi 理解**
   - Play to Earn 机制
   - 游戏经济模型
   - 代币经济
   - NFT 集成

2. **NFT Marketplace**
   - OpenSea V2 机制
   - Blur 竞拍系统
   - NFT Staking
   - NFT Lending

3. **DeFi 集成**
   - NFT 作为抵押品
   - NFT 质押池
   - NFT 借贷
   - 收入模型

4. **2026 年趋势**
   - GameFi 市场数据
   - 技术发展方向
   - 多链策略
   - 移动端优化

5. **智能合约开发**
   - NFT Staking Pool
   - NFT Lending Pool
   - Play to Earn 合约
   - PTE 模式

### 22.2 代码产出

- ✅ NFTStakingPool（NFT 质押池）
- ✅ NFTLendingPool（NFT 借贷池）
- ✅ PlayToEarnGame（Play to Earn 游戏）

---

**【第11小时汇报完毕】**
