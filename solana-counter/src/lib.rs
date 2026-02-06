// Solana 计数器程序库
// 导出所有模块和错误类型

pub mod error;
pub mod instruction;
pub mod state;
pub mod processor;

// 使用 error 模块
pub use error::CounterError;

// 导出指令
pub use instruction::CounterInstruction;

// 导出账户类型
pub use state::Counter;
pub use state::Signer;

// 导出处理器
pub use processor::{Context, InitializeAccounts, IncrementAccounts};

// Solana 程序类型
// 实际程序类型在 entrypoint.rs 中定义

/// 程序版本
pub const VERSION: &str = "0.1.0";

/// 作者
pub const AUTHOR: &str = "Pheglovog";

/// 描述
pub const DESCRIPTION: &str = "A simple counter program for Solana";

/// 程序 ID（部署后替换）
pub const COUNTER_PROGRAM_ID: &str = "COUNTER_PROGRAM_ID";
