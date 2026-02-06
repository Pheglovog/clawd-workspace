// Solana 计数器指令定义
// 定义所有可用的指令和序列化方法

use solana_program::{pubkey::Pubkey, program_error::ProgramError};

#[derive(Debug, Clone, Copy)]
pub enum CounterInstruction {
    /// 初始化计数器
    Initialize,
    /// 增加计数器
    Increment,
    /// 减少计数器
    Decrement,
    /// 设置计数器为特定值
    Set { value: u64 },
    /// 重置计数器
    Reset,
    /// 关闭计数器账户（释放租金）
    Close,
}

impl CounterInstruction {
    /// 将指令编码为字节数组
    pub fn serialize(&self) -> Vec<u8> {
        match self {
            CounterInstruction::Initialize => vec![0],
            CounterInstruction::Increment => vec![1],
            CounterInstruction::Decrement => vec![2],
            CounterInstruction::Set { value } => {
                let mut data = vec![3];
                data.extend_from_slice(&value.to_le_bytes());
                data
            }
            CounterInstruction::Reset => vec![4],
            CounterInstruction::Close => vec![5],
        }
    }

    /// 从字节数组解码为指令
    pub fn try_from_slice(data: &[u8]) -> Result<Self, ProgramError> {
        if data.is_empty() {
            return Err(ProgramError::InvalidInstruction);
        }

        match data[0] {
            0 => Ok(CounterInstruction::Initialize),
            1 => Ok(CounterInstruction::Increment),
            2 => Ok(CounterInstruction::Decrement),
            3 => {
                if data.len() != 9 {
                    return Err(ProgramError::InvalidInstruction);
                }
                let value = u64::from_le_bytes(&data[1..9]);
                Ok(CounterInstruction::Set { value })
            }
            4 => Ok(CounterInstruction::Reset),
            5 => Ok(CounterInstruction::Close),
            _ => Err(ProgramError::InvalidInstruction),
        }
    }
}

#[derive(Debug)]
pub enum Error {
    #[error("Invalid instruction")]
    Invalid,
}

impl std::fmt::Display for Error {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self {
            Self::Invalid => write!(f, "Invalid instruction"),
        }
    }
}

impl std::error::Error for Error {
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        None
    }

    fn description(&self) -> Option<&str> {
        Some(match self {
            Self::Invalid => "Invalid instruction",
        })
    }
}
