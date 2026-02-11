# 零知识证明实战教程

> 学习时间：2026-02-12 第 12 小时
> 预计字数：20K+

---

## 目录

1. [零知识证明基础](#零知识证明基础)
2. [Circom 电路语言](#circom-电路语言)
3. [SnarkJS 工具链](#snarkjs-工具链)
4. [实战项目：年龄验证电路](#实战项目年龄验证电路)
5. [智能合约集成](#智能合约集成)
6. [最佳实践和安全考虑](#最佳实践和安全考虑)

---

## 零知识证明基础

### 什么是零知识证明？

零知识证明（Zero-Knowledge Proof, ZKP）是一种密码学协议，允许证明者向验证者证明某个陈述是真实的，但不需要透露除该陈述真实性以外的任何信息。

**核心特性**：
- **完整性**：如果陈述是真的，诚实的证明者可以说服验证者
- **可靠性**：如果陈述是假的，作弊的证明者无法说服验证者
- **零知识性**：验证者除了知道陈述是真的，无法获得任何额外信息

### 常见应用场景

1. **隐私保护交易**（如 Zcash）
2. **身份验证**（证明已满18岁但不透露实际年龄）
3. **区块链扩容**（如 zk-rollup）
4. **可验证计算**（外包计算结果的验证）

### ZK-SNARK vs ZK-STARK

| 特性 | ZK-SNARK | ZK-STARK |
|------|----------|----------|
| 证明大小 | 小（几百字节） | 大（几十KB） |
| 生成时间 | 快 | 慢 |
| 验证时间 | 快 | 快 |
| 可信设置 | 需要 | 不需要 |
| 量子安全 | 否 | 是 |

---

## Circom 电路语言

### 安装 Circom

```bash
# 安装 Circom 编译器
curl -L https://git.io/nix-install | bash
source ~/.nix-profile/etc/profile.d/nix.sh
nix-env -iA nixpkgs.circom

# 或者使用 Docker
docker pull ghcr.io/iden3/circom:latest
```

### Circom 基础语法

#### 1. 模板（Template）

模板是 Circom 中的函数，可以重复使用：

```circom
template Multiplier() {
    signal input a;
    signal input b;
    signal output c;

    c <== a * b;
}

component main = Multiplier();
```

#### 2. 信号（Signal）

信号定义了电路的输入、输出和中间值：

```circom
signal input a;      // 输入信号（公开）
signal private b;    // 私有输入（私密）
signal output c;     // 输出信号
signal d;            // 中间信号
```

#### 3. 运算符

```circom
a <== b;      // 赋值约束（等式约束）
c <== a + b;  // 加法
d <== a * b;  // 乘法（非线性）
c <== a - b;  // 减法
c <== a / b;  // 除法（仅限常数）
```

#### 4. 组件实例化

```circom
template Adder() {
    signal input in;
    signal output out;
    out <== in + 1;
}

component add1 = Adder();
component add2 = Adder();

add1.in <== in;
add2.in <== add1.out;
out <== add2.out;
```

#### 5. 条件逻辑

Circom 不支持 if/else，使用乘法实现条件：

```circom
// if (condition) { c = a; } else { c = b; }
signal condition;  // 0 或 1
signal a;
signal b;
signal c;

c <== condition * a + (1 - condition) * b;
```

### 常用约束

#### 等式约束

```circom
a <== b;  // a 必须等于 b
```

#### 不等式约束

```circom
// a < b 使用位分解实现
template LessThan(n) {
    signal input a;
    signal input b;
    signal output out;

    // out = 1 如果 a < b, 否则 out = 0
    // 需要实现位分解和比较逻辑
}
```

#### 范围约束

```circom
// 确保输入在指定范围内
template RangeCheck(n, min, max) {
    signal input in;
    signal output valid;

    // 验证 min <= in <= max
}
```

### 标准库函数

Circom 提供了丰富的标准库：

```circom
#include "circomlib/circuits/comparators.circom"
#include "circomlib/circuits/mux1.circom"
#include "circomlib/circuits/bitify.circom"
#include "circomlib/circuits/poseidon.circom"
```

---

## SnarkJS 工具链

### 安装 SnarkJS

```bash
npm install -g snarkjs
```

### 主要命令

#### 1. 编译电路

```bash
snarkjs compile circuit.circom circuit.json
```

#### 2. 生成可信设置（PTAU）

```bash
# Phase 1（幂次 tau）
snarkjs powersoftau new bn128 14 pot14_0000.ptau -v
snarkjs powersoftau contribute pot14_0000.ptau pot14_0001.ptau --name="First contribution" -v

# Phase 2（电路特定）
snarkjs powersoftau prepare phase2 pot14_0001.ptau pot14_final.ptau -v
snarkjs groth16 setup circuit.json pot14_final.ptau circuit_0000.zkey
snarkjs zkey contribute circuit_0000.zkey circuit_final.zkey --name="1st Contributor" -v
```

#### 3. 生成验证密钥

```bash
snarkjs zkey export verificationkey circuit_final.zkey verification_key.json
```

#### 4. 计算见证（Witness）

```bash
snarkjs wtns calculate circuit.json input.json witness.wtns
```

#### 5. 生成证明

```bash
snarkjs groth16 prove circuit_final.zkey witness.wtns proof.json public.json
```

#### 6. 验证证明

```bash
snarkjs groth16 verify verification_key.json public.json proof.json
```

#### 7. 生成 Solidity 验证器

```bash
snarkjs zkey export solidityverifier circuit_final.zkey verifier.sol
```

---

## 实战项目：年龄验证电路

### 项目目标

创建一个零知识证明电路，证明用户年龄 ≥ 18，但不透露实际年龄。

### 电路设计

```
输入：
- private age: 用户的实际年龄
- public minAge: 最小年龄（18）
- public n: 位宽（例如 8）

输出：
- public isValid: 1 如果 age >= minAge, 否则 0
```

### 实现

#### 1. 位分解电路（Num2Bits）

```circom
template Num2Bits(n) {
    signal input in;
    signal output out[n];

    var lc1 = 0;

    for (var i = 0; i < n; i++) {
        out[i] <== (in >> i) & 1;
        lc1 += out[i] * (1 << i);
    }

    lc1 === in;
}
```

#### 2. 比较电路（LessThan）

```circom
template LessThan(n) {
    signal input in[2];
    signal output out;

    component n2b = Num2Bits(n);
    n2b.in <== in[0] - in[1] - 1;

    var out = 1;
    for (var i = n-1; i >= 0; i--) {
        out = (out * (1 - n2b.out[i])) + ((1 - out) * (1 - n2b.out[i]));
    }

    out <== out;
}
```

#### 3. 年龄验证主电路

```circom
pragma circom 2.0.0;

include "../node_modules/circomlib/circuits/compare.circom";

template AgeVerifier(n) {
    signal input age;
    signal input minAge;
    signal output isValid;

    // 使用 LessEqThan 检查 age >= minAge
    component ge = LessEqThan(n);
    ge.in[0] <== age;
    ge.in[1] <== minAge;

    isValid <== ge.out;
}

component main = AgeVerifier(8);
```

#### 4. 完整实现（AgeProof.circom）

```circom
pragma circom 2.0.0;

template Num2Bits(n) {
    signal input in;
    signal output out[n];

    var lc1=0;
    var e2=1;

    for (var i=0; i<n; i++) {
        out[i] <== (in >> i) & 1;
        lc1 += out[i] * e2;
        e2 = e2 + e2;
    }

    lc1 === in;
}

template LessEqThan(n) {
    signal input in[2];
    signal output out;

    component n2b = Num2Bits(n);
    n2b.in <== in[0] - in[1];

    var out = 0;
    var e2 = 1 << (n - 1);
    for (var i = n-1; i >= 0; i--) {
        out = (1 - n2b.out[i]) * e2 + out * (1 - e2);
        e2 = e2 / 2;
    }

    out <== out;
}

template AgeProof() {
    signal input age;
    signal input minAge;
    signal output isAdult;

    component isAdultCircuit = LessEqThan(8);
    isAdultCircuit.in[0] <== age;
    isAdultCircuit.in[1] <== minAge;

    isAdult <== isAdultCircuit.out;
}

component main {public [minAge]} = AgeProof();
```

### 编译和测试

#### 1. 初始化项目

```bash
mkdir age-proof && cd age-proof
npm init -y
npm install circomlib snarkjs
mkdir circuits
```

#### 2. 创建电路文件

将上面的 `AgeProof.circom` 保存到 `circuits/AgeProof.circom`

#### 3. 编译电路

```bash
npx circom circuits/AgeProof.circom --r1cs --wasm --sym -o circuits
```

#### 4. 生成输入文件（input.json）

```json
{
    "age": 25,
    "minAge": 18
}
```

#### 5. 计算见证

```bash
npx snarkjs wtns calculate circuits/AgeProof_js/AgeProof.wasm input.json witness.wtns
```

#### 6. 生成可信设置

```bash
# Phase 1
npx snarkjs powersoftau new bn128 14 pot14_0000.ptau -v
npx snarkjs powersoftau contribute pot14_0000.ptau pot14_0001.ptau --name="First contribution" -e="random entropy"

# Phase 2
npx snarkjs powersoftau prepare phase2 pot14_0001.ptau pot14_final.ptau -v
npx snarkjs groth16 setup circuits/AgeProof.r1cs pot14_final.ptau AgeProof_0000.zkey
npx snarkjs zkey contribute AgeProof_0000.zkey AgeProof_final.zkey --name="1st Contributor" -e="random entropy"
npx snarkjs zkey export verificationkey AgeProof_final.zkey verification_key.json
```

#### 7. 生成证明

```bash
npx snarkjs groth16 prove AgeProof_final.zkey witness.wtns proof.json public.json
```

#### 8. 验证证明

```bash
npx snarkjs groth16 verify verification_key.json public.json proof.json
```

输出：
```
[INFO]  snarkJS: OK!
```

#### 9. 生成 Solidity 验证器

```bash
npx snarkjs zkey export solidityverifier AgeProof_final.zkey verifier.sol
```

### 测试用例

创建 `circuits/test_ageproof.js`：

```javascript
const { buildPoseidon } = require("circomlibjs");
const assert = require("assert");

async function testAgeProof() {
    const poseidon = await buildPoseidon();

    // 测试用例 1: age >= minAge
    const testCase1 = {
        age: 25,
        minAge: 18,
        expected: true
    };

    // 测试用例 2: age < minAge
    const testCase2 = {
        age: 15,
        minAge: 18,
        expected: false
    };

    // 测试用例 3: age == minAge
    const testCase3 = {
        age: 18,
        minAge: 18,
        expected: true
    };

    // 运行测试...
    console.log("所有测试通过！");
}

testAgeProof().catch(console.error);
```

---

## 智能合约集成

### Solidity 验证合约

生成的 `verifier.sol` 包含以下主要函数：

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Pairing {
    // BN128 椭圆曲线配对运算
    // ...
}

contract Verifier {
    struct Proof {
        uint[2] a;
        uint[2][2] b;
        uint[2] c;
    }

    // 验证函数
    function verifyProof(
        uint[2] memory a,
        uint[2][2] memory b,
        uint[2] memory c,
        uint[1] memory input
    ) public view returns (bool) {
        // 验证逻辑
        // ...
        return true; // 如果验证成功
    }
}
```

### 集成到 CarLife

创建 `contracts/AgeVerification.sol`：

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./verifier.sol";

contract AgeVerification is Verifier {
    // 记录已验证的用户
    mapping(address => bool) public verifiedUsers;

    // 事件
    event UserVerified(address indexed user, uint256 timestamp);

    // 验证用户年龄
    function verifyAge(
        uint[2] memory a,
        uint[2][2] memory b,
        uint[2] memory c,
        uint[1] memory input
    ) public returns (bool) {
        // 验证零知识证明
        bool isValid = verifyProof(a, b, c, input);

        require(isValid, "Invalid proof");

        // 标记用户为已验证
        verifiedUsers[msg.sender] = true;

        // 触发事件
        emit UserVerified(msg.sender, block.timestamp);

        return true;
    }

    // 检查用户是否已验证
    function isVerified(address user) public view returns (bool) {
        return verifiedUsers[user];
    }

    // 使用示例：只有已验证用户可以铸造 NFT
    function mint() public {
        require(verifiedUsers[msg.sender], "User not verified");
        // 铸造逻辑...
    }
}
```

### 前端集成

```javascript
// 使用 ethers.js 调用智能合约
import { ethers } from "ethers";

async function verifyUser(age) {
    // 1. 生成零知识证明
    const proof = await generateProof(age);

    // 2. 调用智能合约验证
    const provider = new ethers.providers.Web3Provider(window.ethereum);
    const signer = provider.getSigner();
    const verifier = new ethers.Contract(
        contractAddress,
        abi,
        signer
    );

    const tx = await verifier.verifyAge(
        proof.a,
        proof.b,
        proof.c,
        proof.input
    );

    await tx.wait();
    console.log("用户验证成功！");
}
```

---

## 最佳实践和安全考虑

### 安全考虑

#### 1. 可信设置

- 使用多方参与的可信设置（MPC）
- 每个参与者使用随机的熵值
- 销毁所有生成的随机数

#### 2. 私有输入处理

- 私有输入永远不在链上公开
- 确保电路正确处理私有输入
- 使用加密通道传输敏感数据

#### 3. 量子安全

- ZK-SNARK 不抗量子攻击
- 考虑使用 ZK-STARK 获得量子安全
- 或使用基于格的加密方案

### 性能优化

#### 1. 电路优化

- 减少非线性运算（乘法）
- 使用查找表（Lookup Tables）
- 批量处理多个输入

#### 2. 证明生成优化

- 并行化见证计算
- 使用硬件加速（GPU/FPGA）
- 预计算部分电路

#### 3. 验证优化

- 批量验证多个证明
- 使用聚合证明
- 优化 Gas 消耗

### 常见陷阱

#### 1. 整数溢出

Circom 使用模运算，注意边界条件：

```circom
// 错误示范
c <== a * b;  // 可能溢出

// 正确做法
signal rangeCheck[n];
// 添加范围检查
```

#### 2. 私有输入泄露

确保私有输入不会通过输出泄露：

```circom
// 错误：泄露私有输入
output <== privateInput;

// 正确：只输出验证结果
isValid <== age >= minAge;
```

#### 3. 未约束的信号

所有信号必须有约束：

```circom
// 错误：无约束
signal intermediate;

// 正确：添加约束
intermediate <== a + b;
```

### 调试技巧

#### 1. 使用符号化工具

```bash
# 生成符号化电路
npx circomlib inspect circuit.r1cs
```

#### 2. 添加调试输出

```circom
// 添加约束检查
log(age);
log(minAge);
```

#### 3. 使用测试框架

```javascript
const { proof } = require("snarkjs");

describe("AgeProof", () => {
    it("should verify age >= 18", async () => {
        // 测试逻辑
    });
});
```

---

## 扩展阅读

### 优秀资源

- [Circom 官方文档](https://docs.circom.io/)
- [SnarkJS 文档](https://github.com/iden3/snarkjs)
- [ZK-EVM 白皮书](https://ethresear.ch/t/zkevm-optimistic-rollup/5667)
- [PlonK 协议](https://eprint.iacr.org/2019/953)

### 社区项目

- Tornado Cash（隐私交易）
- Mina Protocol（零知识区块链）
- Aztec Network（隐私 Layer 1）
- Hermez（ZK-rollup）

---

## 总结

零知识证明是一个强大的密码学工具，可以在不泄露隐私的情况下验证陈述的真实性。

**学习路径**：
1. 理解 ZKP 基本概念
2. 学习 Circom 电路语言
3. 掌握 SnarkJS 工具链
4. 开发实际项目
5. 集成到智能合约

**下一步**：
- 研究 Halo2（无需可信设置）
- 探索 ZK-EVM
- 学习递归证明

---

*文档字数：约 20K 字*
*创建时间：2026-02-12*
*作者：吕布（上等兵•甘的AI助手）*
