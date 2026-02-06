// Solana 计数器程序入口点
// 使用 solana_program_entrypoint 库

use solana_program_entrypoint::*;
use solana_security::exitpreprogram::*;

// 引入程序库
solana_program_entrypoint::entrypoint!(process_instruction);

use counter::{error::CounterError, instruction::CounterInstruction, Counter};

pub fn process_instruction(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    data: &[u8],
) -> Result<(), ProgramError> {
    // 将数据解析为指令
    let instruction = CounterInstruction::try_from_slice(data)
        .map_err(|_| CounterError::InvalidInstruction)?;

    // 执行指令
    counter::processor::process_instruction(program_id, accounts, instruction)
        .map_err(|_| CounterError::InvalidInstruction)?;

    Ok(())
}

#[inline(never)]
fn handle_custom_error(error: CounterError) -> u64 {
    error as u64
}

#[cfg(test)]
mod tests {
    use super::*;
    use solana_sdk::{
        account::Account as SolanaAccount,
        pubkey::Pubkey as SolanaPubkey,
        signature::{Keypair as SolanaKeypair, Signer as SolanaSigner},
        transaction::Transaction as SolanaTransaction,
    };

    #[test]
    fn test_instruction_serialization() {
        // 测试指令序列化和反序列化
        let test_cases = vec![
            counter::instruction::CounterInstruction::Initialize,
            counter::instruction::CounterInstruction::Increment,
            counter::instruction::CounterInstruction::Decrement,
            counter::instruction::CounterInstruction::Set { count: 42 },
            counter::instruction::CounterInstruction::Reset,
            counter::instruction::CounterInstruction::Close,
        ];

        for instruction in test_cases {
            let serialized = instruction.serialize();
            let deserialized = counter::instruction::CounterInstruction::try_from_slice(&serialized)
                .expect("Failed to deserialize");

            assert_eq!(instruction, deserialized);
        }
    }
}
