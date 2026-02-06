// Solana 计数器状态模块
// 定义 Counter 账户和 Signer 账户的状态

use solana_program::account_info::AccountInfo;
use solana_program::borsh::{BorshDeserialize, BorshSerialize};
use solana_program::program_error::ProgramError;

/// Counter 账户状态
#[derive(Debug, Clone, BorshSerialize, BorshDeserialize, PartialEq)]
pub struct Counter {
    pub count: u64,
}

/// Signer 账户状态（空，仅用于派生）
#[derive(Debug, Clone, BorshSerialize, BorshDeserialize, PartialEq)]
pub struct Signer {}

/// Counter 账户包装
#[derive(Debug, Clone, Copy)]
pub struct Counter {}

impl Counter {
    pub fn get() -> Self {
        Counter {}
    }

    pub fn add<'a, 'b, 'info>(
        account: &'a AccountInfo<'info, Counter>,
    delta: u64,
    ) -> Result<u64, ProgramError> {
        let counter = &mut account.try_borrow_mut()?;
        counter.count = counter.count.checked_add(delta)
            .map_err(|_| ProgramError::ArithmeticOverflow)?;
        Ok(counter.count)
    }

    pub fn sub<'a, 'b, 'info>(
        account: &'a AccountInfo<'info, Counter>,
        delta: u64,
    ) -> Result<u64, ProgramError> {
        let counter = &mut account.try_borrow_mut()?;
        if counter.count < delta {
            return Err(ProgramError::CounterUnderflow);
        }
        counter.count = counter.count.checked_sub(delta)
            .ok_or(ProgramError::CounterUnderflow)?;
        Ok(counter.count)
    }

    pub fn set<'a, 'b, 'info>(
        account: &'a AccountInfo<'info, Counter>,
        value: u64,
    ) -> Result<u64, ProgramError> {
        let counter = &mut account.try_borrow_mut()?;
        counter.count = value;
        Ok(counter.count)
    }

    pub fn reset<'a, 'b, 'info>(
        account: &'a AccountInfo<'info, Counter>,
    ) -> Result<u64, ProgramError> {
        let counter = &mut account.try_borrow_mut()?;
        counter.count = 0;
        Ok(counter.count)
    }

    pub fn get_value<'a, 'b, 'info>(
        account: &'a AccountInfo<'info, Counter>,
    ) -> Result<u64, ProgramError> {
        let counter = &account.try_borrow_data().map_err(|_| ProgramError::AccountNotInitialized)?;
        Ok(counter.count)
    }
}
