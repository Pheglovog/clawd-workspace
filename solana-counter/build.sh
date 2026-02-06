#!/bin/bash

# Solana 自动化构建和部署脚本
# 使用此脚本编译、构建和部署 Solana 程序

set -e

echo "========================================="
echo "Solana 自动化构建和部署脚本"
echo "========================================="

# 配置变量
PROJECT_DIR="/root/clawd/solana-counter"
PROGRAM_ID="COUNTER_PROGRAM_ID"
NETWORK="devnet"

# 检查项目目录
if [ ! -d "$PROJECT_DIR" ]; then
    echo "错误：项目目录不存在: $PROJECT_DIR"
    exit 1
fi

cd "$PROJECT_DIR"

# 1. 检查 Rust 安装
echo ""
echo "📦 检查 Rust 安装..."
if ! command -v rustc &> /dev/null; then
    echo "错误：Rust 未安装"
    echo "请运行以下命令安装 Rust:"
    echo "  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y"
    exit 1
fi

RUST_VERSION=$(rustc --version)
echo "✅ Rust 版本: $RUST_VERSION"

# 2. 检查 Cargo 版本
CARGO_VERSION=$(cargo --version)
echo "✅ Cargo 版本: $CARGO_VERSION"

# 3. 尝试构建程序
echo ""
echo "🔧 尝试构建 Solana 程序..."
echo "========================================="

# 检查必要的依赖
echo "📦 检查依赖..."

# 创建构建输出目录
mkdir -p "$PROJECT_DIR/target/deploy"

# 尝试构建（可能会失败，因为缺少 Solana CLI）
echo "🔨 运行 cargo build-bpf..."
cargo build-bpf 2>&1 | tee build.log

# 检查构建状态
if [ $? -eq 0 ]; then
    echo "✅ 构建成功！"
    echo ""
    echo "构建产物："
    ls -lh "$PROJECT_DIR/target/bpfel-unknown-unknown/release/solana_counter.so" || \
    ls -lh "$PROJECT_DIR/target/deploy/solana_counter.so"
else
    echo "⚠️  构建失败"
    echo ""
    echo "构建错误:"
    tail -20 build.log
fi

# 4. 部署程序（如果 Solana CLI 可用）
echo ""
echo "🚀 部署程序到 $NETWORK..."
echo "========================================="

if command -v solana &> /dev/null; then
    # 配置 Solana CLI
    solana config set --url "$NETWORK"

    # 获取程序路径
    PROGRAM_PATH="$PROJECT_DIR/target/bpfel-unknown-unknown/release/solana_counter.so"
    if [ ! -f "$PROGRAM_PATH" ]; then
        PROGRAM_PATH="$PROJECT_DIR/target/deploy/solana_counter.so"
    fi

    if [ ! -f "$PROGRAM_PATH" ]; then
        echo "错误：找不到程序文件: $PROGRAM_PATH"
        exit 1
    fi

    echo "程序路径: $PROGRAM_PATH"

    # 部署程序
    PROGRAM_ID=$(solana program deploy "$PROGRAM_PATH" \
        --program-id "$PROGRAM_ID" \
        --keypair "$HOME/.config/solana/id.json" \
        2>&1)

    if [ $? -eq 0 ]; then
        echo "✅ 程序部署成功！"
        echo ""
        echo "程序 ID: $PROGRAM_ID"
    else
        echo "⚠️  程序部署失败"
        echo ""
        echo "可能原因："
        echo "  1. Solana CLI 未正确安装"
        echo "  2. 网络问题"
        echo "  3. 钱包配置问题"
    fi
else
    echo "⚠️  Solana CLI 未安装"
    echo ""
    echo "请先安装 Solana CLI："
    echo "  sh -c \"\$(curl -sSfL https://release.solana.com/v1.10/install/solana-install-init.sh)\""
fi

# 5. 创建测试密钥
echo ""
echo "🔑 创建测试密钥..."
echo "========================================="

if command -v solana-keygen &> /dev/null; then
    mkdir -p "$PROJECT_DIR/tests"
    cd "$PROJECT_DIR/tests"

    # 创建测试密钥
    solana-keygen new --outfile keypair-test.json --no-bip39-passphrase

    if [ -f "keypair-test.json" ]; then
        echo "✅ 测试密钥创建成功！"
        echo ""
        echo "公钥:"
        solana-keygen pubkey keypair-test.json
        echo ""
        echo "私钥文件:"
        cat keypair-test.json
    else
        echo "⚠️  测试密钥创建失败"
    fi
else
    echo "⚠️  solana-keygen 未找到"
fi

# 6. 运行测试
echo ""
echo "🧪 运行测试..."
echo "========================================="

if command -v solana-program-test &> /dev/null; then
    cd "$PROJECT_DIR"
    
    # 配置测试环境
    export COUNTER_PROGRAM_ID=$PROGRAM_ID
    
    echo "使用程序 ID: $COUNTER_PROGRAM_ID"
    
    # 运行测试
    echo ""
    echo "运行单元测试..."
    cargo test-bpf 2>&1 | tee test.log
    
    # 检查测试状态
    if [ $? -eq 0 ]; then
        echo "✅ 测试通过！"
    else
        echo "⚠️  测试失败"
        echo ""
        echo "测试错误:"
        tail -20 test.log
    fi
else
    echo "⚠️  solana-program-test 未安装"
fi

# 7. 交互式提示
echo ""
echo "========================================="
echo "💡 交互式提示"
echo "========================================="
echo ""
echo "手动构建程序:"
echo "  cd $PROJECT_DIR"
echo "  cargo build-bpf"
echo ""
echo "部署程序:"
echo "  solana program deploy target/bpfel-unknown-unknown/release/solana_counter.so --program-id $PROGRAM_ID"
echo ""
echo "运行测试:"
echo "  export COUNTER_PROGRAM_ID=$PROGRAM_ID"
echo "  cargo test-bpf"
echo ""
echo "查看程序账户:"
echo "  solana program show $PROGRAM_ID"
echo ""
echo "查看所有账户:"
echo "  solana account"
echo ""
echo "========================================="
echo "✅ 脚本执行完成！"
echo "========================================="
