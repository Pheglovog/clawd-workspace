// Solana 计数器错误类型定义
// 自定义错误处理

use solana_program::program_error::ProgramError;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CounterError {
    /// 账户已经初始化
    #[error("Counter already initialized")]
    AlreadyInitialized,

    /// 账户未初始化
    #[error("Counter account not initialized")]
    NotInitialized,

    /// 计数器下溢（不能小于 0）
    #[error("Counter cannot be decremented below 0")]
    Underflow,

    /// 无效的指令
    #[error("Invalid instruction")]
    Invalid,

    /// 算术溢出
    #[error("Arithmetic overflow")]
    ArithmeticOverflow,
}

impl std::fmt::Display for CounterError {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self {
            CounterError::AlreadyInitialized => write!(f, "Counter already initialized"),
            CounterError::NotInitialized => write!(f, "Counter not initialized"),
            CounterError::Underflow => write!(f, "Counter underflow"),
            CounterError::Invalid => write!(f, "Invalid instruction"),
            CounterError::ArithmeticOverflow => write!(f, "Arithmetic overflow"),
        }
    }
}

impl From<CounterError> for ProgramError {
    fn from(error: CounterError) -> Self {
        Self::Custom(error.into())
    }
}
